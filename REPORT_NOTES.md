# 1 užduotis — Docker: kūrimas, skenavimas, sustiprinimas ir publikavimas

**Studentas:** Mateuš Juchnevič  
**Įmonė:** UAB „VėjoEnergija“ (mokomasis scenarijus)  
**Skenavimo data:** [įrašyti realią datą]  
**Aplinkos informacija:** Arch Linux [versija], Docker [versija], Trivy [versija]

## 1.1. Tikslas ir aplikacija

Sukurtas demonstracinis vėjo jėgainių stebėsenos portalas, rodantis išgalvotų įrenginių būklę ir galią. Puslapį pateikia Flask; aplikacija turi `/health` patikros maršrutą ir `/api/turbines` JSON API. Tikslas — palyginti nesaugaus ir sustiprinto konteinerio konfigūraciją, atrastus pažeidžiamumus bei vykdymo apribojimus.

[E01 — Docker veikia]

## 1.2. Nesaugus Dockerfile

| Klaida | Eilutė / nustatymas | Kodėl pavojinga |
|---|---|---|
| Sena bazinė versija | `python:3.11.9-bookworm` | Joje gali būti senų OS ir Python paketų su žinomais pažeidžiamumais; tikrinama skeneriu. |
| Root naudotojas | nėra `USER` | Kompromitavus aplikaciją procesas konteineryje veiktų su didesnėmis teisėmis. |
| Paslaptis `ENV` | `DEMO_API_KEY` (tik netikras pavyzdys) | `docker inspect` gali parodyti kintamojo reikšmę. |
| Nereikalingi paketai | `vim curl net-tools` | Didėja atakos paviršius ir image dydis. |
| `ADD .` | visas build kontekstas | Išplečiamas kopijuojamų failų rinkinys, o `COPY` šiuo atveju būtų aiškesnis. |
| Nereikalingas 22 prievadas | `EXPOSE 22` | Klaidingai dokumentuoja nenaudojamą SSH prievadą; pats `EXPOSE` jo viešai neatidaro. |
| Development serveris | `python app.py` | Nėra produkcinis WSGI serveris. |

[E02 — Dockerfile.insecure]
[E03 — veikiantis nesaugus konteineris]

## 1.3. Skenavimas prieš sustiprinimą

[E04 — Trivy santrauka]

| CVE ID | Paketas ir įdiegta versija | CVSS / severity | Fiksuota versija | Ar paveiktas funkcionalumas naudojamas? |
|---|---|---|---|---|
| [tikras CVE #1] | [tikras paketas] | [iš šaltinio] | [jei yra] | [argumentuotas vertinimas] |
| [tikras CVE #2] | [tikras paketas] | [iš šaltinio] | [jei yra] | [argumentuotas vertinimas] |
| [tikras CVE #3] | [tikras paketas] | [iš šaltinio] | [jei yra] | [argumentuotas vertinimas] |

Svarbu: pažeidžiamo paketo buvimas image nereiškia, kad konkreti klaida yra pasiekiama per mūsų aplikaciją. Būtina patikrinti CVE aprašymą, išnaudojimo sąlygas ir tai, ar atitinkama funkcija vykdoma.

[E05 — 3 CVE analizės įrodymai]

## 1.4. Sustiprintas Dockerfile ir vykdymas

Naudojama konkreti Python slim versija, du build etapai, atskiras ne-root naudotojas su UID 10001, HEALTHCHECK ir naujesnės aplikacijos priklausomybės. Nereikalingų diagnostikos paketų ir demonstracinės API rakto reikšmės galutiniame image nėra. Papildomai `docker run` metu taikomas nekeičiamas failų sistemos sluoksnis, pašalinamos Linux capabilities, neleidžiama įgyti naujų privilegijų ir ribojami ištekliai.

[E06 — Dockerfile.hardened, health ir portalas]
[E07 — docker inspect apribojimai]

## 1.5. Rezultatai prieš ir po

| Matuojamas dydis | Nesaugus image | Sustiprintas image |
|---|---|---|
| Critical CVE | [skaičius] | [skaičius] |
| High CVE | [skaičius] | [skaičius] |
| Medium CVE | [skaičius] | [skaičius] |
| Low CVE | [skaičius] | [skaičius] |
| Image dydis | [MB] | [MB] |
| Vartotojas | root | 10001:10001 |
| Demonstracinis `DEMO_API_KEY` | Yra ENV | Nėra |

[E08 ir E09 — pakartotinis skenavimas ir palyginimas]

Image dydis, CVE skaičius ir galimi likę pažeidžiamumai turi būti įrašyti iš **tikrų komandų**; nėra iš anksto žinomi.

## 1.6. DockerHub publikacija

Viešai įkeltas **tik** sustiprintas image.  
Nuoroda: [įklijuoti tikrą DockerHub URL]

[E10 — DockerHub ir docker push]

## 1.7. Atsakymai į teorinius klausimus

**Kodėl pavojingas `--privileged`?** `--privileged` konteineriui suteikia žymiai daugiau teisių, prieigos prie įrenginių ir sumažina Linux saugumo mechanizmų ribojimus. Jei tokia aplikacija būtų kompromituota, užpuolikas galėtų lengviau paveikti Docker host sistemą.

**Kodėl pavojingas atidengtas Docker daemon?** Docker API, ypač jei prieinama be autentifikavimo ir tinkamos prieigos kontrolės, leidžia valdyti konteinerius ir host resursus. Užpuolikas, galintis duoti komandas Docker daemon procesui, praktiškai gali įgyti labai aukštas teises serveryje.

**Konteineris ir VM:** konteineriai dalijasi host Linux branduoliu, bet izoliuoja procesus, failų sistemą ir tinklo aplinką. Virtuali mašina paprastai turi atskirą svečio OS branduolį ir izoliuojama per hipervizorių; dėl to izoliacijos riba kitokia, nors abi technologijos gali turėti pažeidžiamumų.

## 1.8. Išvada (pataisyti pagal realius rezultatus)

Pradinis image turėjo kelias tyčines konfigūracijos klaidas: root naudotoją, perteklinius paketus ir netikrą API raktą ENV. Trivy skenavimo metu aptikta [skaičius] pažeidžiamumų, o po atnaujinimo liko [skaičius]. Sustiprintas image veikia su ne-root naudotoju ir papildomais Docker vykdymo apribojimais, kuriuos patvirtina `docker inspect` išvestis. Likusi rizika yra [konkretūs neištaisyti CVE, trečiųjų šalių priklausomybės ar netinkama host konfigūracija].
