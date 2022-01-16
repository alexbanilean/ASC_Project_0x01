# ASC_Proiect_0x01

# Introducere

**Cerința proiectului:**  

Creați un executor RISC-V și executați codul din fiecare fișier .mc.

---

### Membrii echipei

* Bănilean Alexandru-Ioan (grupa 152) 

* Ivașciuc Iancu Teodor (grupa 131)

---

# Mod de utilizare

### Mediu de lucru
- Python 3.9.0

### Metoda de rulare
Programul se rulează în modul următor, direct cu interpretatorul python:

```
python3 executor.py
```

---

**Mențiuni:**

Numele fișierelor .mc se află într-o listă în cadrul script-ului. 
Pentru a-l putea executa cu succes, acestea trebuie să fie în același fișier cu ```executor.py```.

Am început rularea programului de la eticheta \<userstart\> (de acolo apare și aceea inițializare a program counter-ului PC), curățând regiștrii (reținuți într-un array) la începerea fiecărei execuții pe fișier. 

În rezolvare am implementat doar funcțiile necesare pentru executarea testelor atașate.


# Articole folosite
- [RISC-V instructions format](https://inst.eecs.berkeley.edu/~cs61c/resources/su18_lec/Lecture7.pdf)
- [RISC-V ISA overview](http://users.ece.cmu.edu/~jhoe/course/ece447/S18handouts/L02.pdf)
- [RISC-V Reference Data Card ("Green Card")](https://inst.eecs.berkeley.edu/~cs61c/fa17/img/riscvcard.pdf)
