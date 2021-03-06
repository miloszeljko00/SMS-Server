from functools import wraps
from flask import Flask, render_template, request, url_for, redirect, Response
from utils import Database, log
import json
import sqlite3
import HTML
import serial
from curses import ascii
from time import gmtime, strftime, sleep
import sys
Nivo1IP = []
Nivo2IP = []
Nivo3IP = []
Nivo4IP = []
Nivo5IP = []

app = Flask(__name__)


class SMS:
    def __init__(self, baudrate=115200, device="/dev/ttyUSB0", pin=2391):
        self.modem = serial.Serial(device, baudrate, timeout=5)
        print "[INFO ] Starting connection with modem at " + device + "..."

        self.modem.write(b'AT\r')
        self.getresponse(0)
        response = self.modem.read(4)
        if "OK" in response:
            print "[INFO ] Connected successfully."
            self.changeToTextMode()
            log("warning", "modem", "Konekcija sa modemom uspesno uspostavljena")
        elif "NO CARRIER" in response:
            log("danger", "error", "Na SIM katici nema 3G konekcije")
            print "[ERROR] There is no 3G connection! :/"
        else:
            log("danger", "error", "Doslo je do greske prilikom postavljanja modema")
            print "[ERROR] Something went wrong :("

    def send(self, receiver, message):
        if receiver is not None and message is not None:
            print "[DEBUG] Sending SMS with details: "
            print "Reciever: %s" % receiver
            print "Message: %s" % message
	    time222 = strftime("%Y-%m-%d %H:%M:%S", gmtime())
            print "Time: %s", time222

            self.modem.write(b'AT+CMGS="%s"\r' % receiver)
            sleep(0.05)
            self.modem.write(b'%s\r' % message)
            sleep(0.05)
            self.modem.write(ascii.ctrl('z'))
            sleep(0.05)
            response = self.modem.readlines()
            if "+CMGS" in response[-3]:
                print "[INFO ] SMS sent successfully!"
            	log("success", "sms", "Poruka sa sledecim detaljima je uspesno poslata", more="Primalac: %s Poruka: %s" % (receiver, message,))
            else:
                print "[ERROR] Something went wrong while sending SMS!"
            	log("danger", "sms", "Doslo je do greske prilikom slanja poruke", more="Primalac: %s Poruka: %s" % (receiver, message))
        else:
            print ""

  

    def changeToTextMode(self):
        print "[INFO ] Setting module to text mode"
        self.modem.write(b'AT+CMGF=1\r')
        response = self.getresponse(1)
        if "OK" in response:
            print "[INFO ] Text Mode activated."
        else:
            print "[WARNING] Could not set modem to text mode, text mode might be active!"

    def disconnect(self):
        self.modem.close()

    def getresponse(self, skip):
        for lines in range(0, skip):
            while True:
                ch = self.modem.read(1)
                if ch == '\r':
                    break
        buf = ""
        while True:
            ch = self.modem.read(1)
            if ch == '\r':
                break
            buf += ch
        return buf


@app.route('/',methods=['GET'])
def index():
	return render_template("index.html")
		


@app.route('/login',methods=['POST'])
def login():
	if request.method == 'POST':
		user=request.form['username']
		pw=request.form['password']
	conn = sqlite3.connect('databases/sms.db')
	c = conn.cursor()
	c.execute("SELECT detalji.*,tip.nivo,korisnici.id FROM detalji,korisnici,tip WHERE  detalji.userID = korisnici.id AND tip.id = korisnici.tipID AND detalji.username=?", (user,))
	korisnik = c.fetchall()
	if any(korisnik) :
		for row in korisnik :
			lozinka=row[2]
			nivo=row[3]
			print lozinka
			if lozinka == pw:
				if not (str(request.remote_addr) in Nivo1IP or str(request.remote_addr) in Nivo2IP or str(request.remote_addr) in Nivo3IP or str(request.remote_addr) in Nivo4IP):
					if(nivo==5):
						Nivo5IP.append(str(request.remote_addr))
						return redirect(url_for('admin'))
					elif(nivo==4):
						Nivo4IP.append(str(request.remote_addr))
						return redirect(url_for('home'))
					elif(nivo==3):
						Nivo3IP.append(str(request.remote_addr))
						return redirect(url_for('home'))
					elif(nivo==2):
						Nivo2IP.append(str(request.remote_addr))
						return redirect(url_for('home'))
					elif(nivo==1):
						Nivo1IP.append(str(request.remote_addr))
						return redirect(url_for('home'))
				else:
					try:
						Nivo1.remove(str(request.remote_addr))
					except:
						pass

					try:
						Nivo2.remove(str(request.remote_addr))
					except:
						pass

					try:
						Nivo3.remove(str(request.remote_addr))
					except:
						pass

					try:
						Nivo4.remove(str(request.remote_addr))
					except:
						pass

					try:
						Nivo5.remove(str(request.remote_addr))
					except:
						pass		
					Nivo1IP.append(str(request.remote_addr))
					return redirect(url_for('admin'))
			else:
				return redirect(url_for("index"))
	else:
		return redirect(url_for("index"))
			
	

@app.route('/home',methods=['GET'])
def home():
	if (str(request.remote_addr) in Nivo1IP or str(request.remote_addr) in Nivo2IP or str(request.remote_addr) in Nivo3IP or str(request.remote_addr) in Nivo4IP):
		global nivo
		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
		c.execute("SELECT * FROM korisnici ORDER BY prezime,ime")
		kontakti=c.fetchall()
		c.execute("SELECT * FROM Sabloni")
		sablons=c.fetchall()
		if (str(request.remote_addr) in Nivo1IP):
			c.execute("SELECT * FROM tip WHERE Podgrupa=? AND nivo<=?",(2,1),)
			nastavno=c.fetchall()
			c.execute("SELECT * FROM tip WHERE Podgrupa=? AND nivo<=?",(1,1),)
			nenastavno=c.fetchall()
		if (str(request.remote_addr) in Nivo2IP):
			c.execute("SELECT * FROM tip WHERE Podgrupa=? AND nivo<=?",(2,2),)
			nastavno=c.fetchall()
			c.execute("SELECT * FROM tip WHERE Podgrupa=? AND nivo<=?",(1,2),)
			nenastavno=c.fetchall()
		if (str(request.remote_addr) in Nivo3IP):
			c.execute("SELECT * FROM tip WHERE Podgrupa=? AND nivo<=?",(2,3),)
			nastavno=c.fetchall()
			c.execute("SELECT * FROM tip WHERE Podgrupa=? AND nivo<=?",(1,3),)
			nenastavno=c.fetchall()
		if (str(request.remote_addr) in Nivo4IP):
			c.execute("SELECT * FROM tip WHERE Podgrupa=? AND nivo<=?",(2,4),)
			nastavno=c.fetchall()
			c.execute("SELECT * FROM tip WHERE Podgrupa=? AND nivo<=?",(1,4),)
			nenastavno=c.fetchall()
		
		
		
		
		print sablons
		conn.close()
		return render_template("home.html",imena=kontakti,templates=sablons,nastavno=nastavno,nenastavno=nenastavno)
	else:
		return redirect(url_for('index'))

@app.route('/admin',methods=['GET'])
def admin():
	if str(request.remote_addr) in Nivo5IP:
		return render_template("admin.html")
	else:
		return redirect(url_for('index'))

@app.route("/korisnici",methods=['GET','POST'])
def korisnici():
	if str(request.remote_addr) in Nivo5IP:
		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
		c2 = conn.cursor()
		c.execute("SELECT * FROM detalji")
		korisnik = c.fetchall()
		if any(korisnik) :
			skip=0
			for row in korisnik :
				if(skip==1):
					userID=row[0]
					username=row[1]
					lozinka=row[2]
					c2.execute("SELECT k.ime, k.prezime, t.naziv FROM korisnici k,  tip t WHERE k.tipID = t.id AND k.id=? ORDER BY k.prezime,k.ime", (userID,))
					imeprezime = c2.fetchall()
					for row in imeprezime:
						ime=row[0]
						prezime=row[1]
						tip = row[2]
					korisnici = korisnici + ((userID,ime,prezime,username,lozinka,tip),)
				if(skip==0):
					userID=row[0]
					username=row[1]
					lozinka=row[2]
					c2.execute("SELECT k.ime, k.prezime, t.naziv FROM korisnici k,  tip t WHERE k.tipID = t.id AND k.id=? ORDER BY k.prezime,k.ime", (userID,))
					imeprezime = c2.fetchall()
					for row in imeprezime:
						ime=row[0]
						prezime=row[1]
						tip = row[2]
					korisnici = ((userID,ime,prezime,username,lozinka,tip),)
				skip=1
			print korisnici

		c2.execute("SELECT * FROM tip")
		access=c2.fetchall()
		conn.close()	
	
		return render_template('ap-users.html',korisnici = korisnici,tipovi=access)
	else:
		return redirect(url_for('index'))
	



@app.route("/korisnici/edit",methods=['GET','POST'])

def edit():
	if str(request.remote_addr) in Nivo5IP:
		userID = request.form['id']
		username = request.form['username']
		password = request.form['password']
		ime = request.form['ime']
		prezime = request.form['prezime']
		tipID = request.form['tipID']

		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
		c2 = conn.cursor()

		c.execute("UPDATE detalji SET username =?, password =? WHERE userID =?", (username,password,userID,))
		c.execute("UPDATE korisnici SET ime =?, prezime =?,tipID=? WHERE id =?", (ime,prezime,tipID,userID,))
		conn.commit()
	
		conn.close()
		return redirect(url_for('korisnici'))
	else:
		return redirect(url_for('index'))

@app.route("/korisnici/izbrisi",methods=['GET','POST'])
def izbrisi():
	if str(request.remote_addr) in Nivo5IP:
		userID = request.form['id']
	

		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
	

		c.execute("DELETE FROM detalji WHERE userID =?", (userID,))
		conn.commit()
	
		conn.close()
		return redirect(url_for('korisnici'))
	else:
		return redirect(url_for('index'))

@app.route("/home/slanje",methods=['GET','POST'])
def slanje():
	if (str(request.remote_addr) in Nivo1IP or str(request.remote_addr) in Nivo2IP or str(request.remote_addr) in Nivo3IP or str(request.remote_addr) in Nivo4IP):
		primaoci = request.form['send_sms_to']
		poruka = request.form['message']
		if(primaoci== 'all'):
			phone = SMS()
			conn = sqlite3.connect('databases/sms.db')
			c = conn.cursor()
			c.execute("SELECT telefon FROM korisnici")
			brojevi = c.fetchall()
			for broj in brojevi:
				phone.send(broj[0],poruka)
		
		elif(primaoci == 'selected_groups_teachers'):
			phone = SMS()
			conn = sqlite3.connect('databases/sms.db')
			c = conn.cursor()
		
			status=request.form.getlist('status')

			print status
				
			for row in status:
				c.execute("SELECT telefon FROM korisnici WHERE tipID=?",(row[0],))
				brojevi = c.fetchall()
				for broj in brojevi:
					phone.send(broj[0],poruka)

		elif(primaoci == 'selected_groups_others'):
			phone = SMS()
			conn = sqlite3.connect('databases/sms.db')
			c = conn.cursor()
		
			status=request.form.getlist('status')

			print status

			for row in status:
				print row
				i = int(row)
				print i
				c.execute("SELECT telefon FROM korisnici WHERE tipID=?",(row,))
				brojevi = c.fetchall()
				for broj in brojevi:
					phone.send(broj[0],poruka)
		else:
			phone = SMS()
			conn = sqlite3.connect('databases/sms.db')
			c = conn.cursor()
		
			status=request.form.getlist('status')

			print status
			for row in status:
					print row
					i = int(row)
					print i
					c.execute("SELECT telefon FROM korisnici WHERE id=?",(row,))
					brojevi = c.fetchall()
					for broj in brojevi:
						phone.send(broj[0],poruka)
					

		conn.close()
		phone.disconnect()
		return redirect(url_for('home'))
	else:
		return redirect(url_for('index'))

@app.route("/korisnici/novi",methods=['GET','POST'])
def novi():
	if str(request.remote_addr) in Nivo5IP:
		username = request.form['username']
		password = request.form['password']
		ime = request.form['ime']
		prezime = request.form['prezime']
		tip = request.form['tipID']
	
		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
		c2= conn.cursor()
		c2.execute("SELECT id FROM korisnici WHERE ime = ? AND prezime =?",(ime,prezime,))
		korisnik=c2.fetchall()
		if any (korisnik):
			for neko in korisnik:
				c.execute("INSERT INTO detalji (userID,username,password) VALUES(?,?,?)",(neko[0],username,password))
				conn.commit()
		else:
			c.execute("INSERT INTO korisnici (ime,prezime,tipID) VALUES(?,?,?)",(ime,prezime,tip))
			conn.commit()
			c.execute("SELECT id FROM korisnici WHERE ime = ? AND prezime =?",(ime,prezime))
			ajdi = c.fetchone()
			c.execute("INSERT INTO detalji (userID,username,password) VALUES(?,?,?)",(ajdi[0],username,password))
			conn.commit()
		
		c2.execute("SELECT * FROM tip")
		access=c2.fetchall()
		conn.close()
		return redirect(url_for('korisnici'))
	else:
		return redirect(url_for('index'))

@app.route("/logs",methods=['GET','POST'])
def logs():
	if str(request.remote_addr) in Nivo5IP:
		with open('logs.json') as data_file:    
				logovi = json.load(data_file)["logs"]
		return render_template('logs.html', logs=logovi)
	else:
		return redirect(url_for('index'))


@app.route("/kontakti",methods=['GET','POST'])
def kontakti():
	if str(request.remote_addr) in Nivo5IP:
		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
		c.execute("SELECT k.* FROM korisnici k ORDER BY k.prezime,k.ime")
		kontakt = c.fetchall()
		if any(kontakt) :
			skip=0
			for row in kontakt :
				if(skip==1):
					userID=row[0]
					ime=row[1]
					prezime=row[2]
					broj=row[3]
					tip=row[4]
					c.execute("SELECT naziv FROM tip WHERE id=?",(tip,))
					grupa = c.fetchone()
					korisnici = korisnici + ((userID,ime,prezime,broj,grupa[0]),)
				if(skip==0):
					userID=row[0]
					ime=row[1]
					prezime=row[2]
					broj=row[3]
					tip=row[4]
					c.execute("SELECT naziv FROM tip WHERE id=?",(tip,))
					grupa = c.fetchone()
					korisnici =((userID,ime,prezime,broj,grupa[0]),)
				skip=1
			print korisnici

		c.execute("SELECT * FROM tip")
		access=c.fetchall()
		conn.close()
	
		return render_template('ap-contacts.html',korisnici = korisnici, tipovi = access)
	else:
		return redirect(url_for('index'))



@app.route("/kontakti/novi2",methods=['GET','POST'])
def novi2():
	if str(request.remote_addr) in Nivo5IP:
		ime = request.form['ime']
		prezime = request.form['prezime']
		broj = request.form['broj']
		tip = request.form['tipID']
	
		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
		c.execute("INSERT INTO korisnici (ime,prezime,telefon,tipID) VALUES(?,?,?,?)",(ime,prezime,broj,tip))
		conn.commit()
		c.execute("SELECT * FROM tip")
		access=c.fetchall()
		conn.close()
		return redirect(url_for('kontakti'))
	else:
		return redirect(url_for('index'))

@app.route("/kontakti/edit2",methods=['GET','POST'])
def edit2():
	if str(request.remote_addr) in Nivo5IP:
		ime = request.form['ime']
		prezime = request.form['prezime']
		broj = request.form['broj']
		tip = request.form['tipID']
		ajdi = request.form['id']

		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
		c2 = conn.cursor()

		c.execute("UPDATE korisnici SET ime =?, prezime =?, telefon=?, tipID=? WHERE id =?", (ime,prezime,broj, tip, ajdi,))
		conn.commit()
	
		conn.close()
		return redirect(url_for('kontakti'))
	else:
		return redirect(url_for('index'))

@app.route("/kontakti/izbrisi2",methods=['GET','POST'])
def izbrisi2():
	if str(request.remote_addr) in Nivo5IP:
		userID = request.form['id']
	

		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
	

		c.execute("DELETE FROM korisnici WHERE id =?", (userID,))
		conn.commit()
	
		conn.close()
		return redirect(url_for('kontakti'))
	else:
		return redirect(url_for('index'))
@app.route("/logout",methods=['GET','POST'])
def logout():
		try:
			Nivo1.remove(str(request.remote_addr))
		except:
			pass
		
		try:
			Nivo2.remove(str(request.remote_addr))
		except:
			pass

		try:
			Nivo3.remove(str(request.remote_addr))
		except:
			pass

		try:
			Nivo4.remove(str(request.remote_addr))
		except:
			pass

		try:
			Nivo5.remove(str(request.remote_addr))
		except:
			pass		

		return redirect(url_for('index'))

@app.route("/sabloni",methods=['GET','POST'])
def sabloni():
	if str(request.remote_addr) in Nivo5IP:
		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
		c.execute("SELECT * FROM sabloni")
		sablons = c.fetchall()
		if any(sablons) :
			skip=0
			for row in sablons :
				if(skip==1):
					sablon=row[0]
					sadrzaj=row[1]
					sablonID=row[2]
					sabloni = sabloni + ((sablon,sadrzaj,sablonID),)
				if(skip==0):
					sablon=row[0]
					sadrzaj=row[1]
					sablonID=row[2]
					sabloni = ((sablon,sadrzaj,sablonID),)
				skip=1
			print sabloni
			conn.close()
			return render_template('ap-sabloni.html',sabloni=sabloni)
		else:
			return redirect(url_for('index'))

@app.route("/kontakti/izbrisiSablon",methods=['GET','POST'])
def izbrisiSablon():
	if str(request.remote_addr) in Nivo5IP:
		sablonID = request.form['id']
	

		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
	

		c.execute("DELETE FROM sabloni WHERE sablonID =?", (sablonID,))
		conn.commit()
	
		conn.close()
		return redirect(url_for('sabloni'))
	else:
		return redirect(url_for('index'))


@app.route("/kontakti/editSablon",methods=['GET','POST'])
def editSablon():
	if str(request.remote_addr) in Nivo5IP:
		sablon = request.form['sablon']
		sadrzaj = request.form['sadrzaj']
		ajdi = request.form['id']

		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
		c2 = conn.cursor()

		c.execute("UPDATE sabloni SET sablon =?, sadrzaj =? WHERE sablonID =?", (sablon,sadrzaj, ajdi,))
		conn.commit()
	
		conn.close()
		return redirect(url_for('sabloni'))
	else:
		return redirect(url_for('index'))

@app.route("/kontakti/noviSablon",methods=['GET','POST'])
def noviSablon():
	if str(request.remote_addr) in Nivo5IP:
		sablon = request.form['sablon']
		sadrzaj = request.form['sadrzaj']
	
		conn = sqlite3.connect('databases/sms.db')
		c = conn.cursor()
		c.execute("INSERT INTO sabloni (sablon,sadrzaj) VALUES(?,?)",(sablon,sadrzaj))
		conn.commit()
		conn.close()
		return redirect(url_for('sabloni'))
	else:
		return redirect(url_for('index'))




if __name__ == '__main__':
	app.run(debug=True, host='0.0.0.0',port=5000)
