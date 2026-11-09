# VėjoEnergija Security Lab — 1 užduotis (Docker)

**Studentas:** Mateuš Juchnevič  
**Aplinka:** Arch Linux, Docker Engine  
**Paskirtis:** tik asmeninė mokomoji laboratorija. Visi jėgainių duomenys yra išgalvoti.

Šis projektas turi dvi to paties portalo konteinerio versijas:

- `Dockerfile.insecure` — sąmoningai nesaugi konfigūracija, skirta tik parodyti ir ištirti trūkumus vietinėje aplinkoje;
- `Dockerfile.hardened` — mažesnė, ribotomis privilegijomis veikianti versija, kurią leidžiama viešinti DockerHub.

**Svarbu:** net ir sustiprinto image saugumas nėra garantuotas. CVE skaičiai priklauso nuo skenavimo datos ir duomenų bazės; visada remkis tik savo Trivy išvestimi.

## 1. Patikrink, ar Docker įdiegtas

Arch Linux terminale vykdyk paeiliui:

```bash
docker --version
sudo docker info
systemctl is-active docker
```

Jeigu Docker neįdiegtas arba tarnyba neveikia, naudok:

```bash
sudo pacman -Syu docker docker-buildx trivy jq
sudo systemctl enable --now docker.service
sudo docker run --rm hello-world
```

Jei Docker jau veikia, bet trūksta Trivy ar jq:

```bash
sudo pacman -Syu trivy jq
```

**Įrodymas E01:** terminalas su `docker --version` ir `sudo docker run --rm hello-world` sėkmės tekstu.

Toliau naudojame `sudo docker`, kad nereikėtų pridėti naudotojo į privilegijuotą `docker` grupę. Naršyklėje aplikaciją atidarysime tik `127.0.0.1`, o ne viešame IP adrese.

## 2. Atidaryk projektą

Išarchyvuok `vejoenergija-task1.zip` į pasirinktą savo katalogą. Tada atsidaryk terminalą išarchyvuotame `vejoenergija-task1` aplanke ir vykdyk `pwd`, kad įsitikintum, jog esi teisingoje vietoje.

Projekto turinys:

```text
vejoenergija-task1/
├── app.py
├── templates/index.html
├── requirements.txt
├── requirements.insecure.txt
├── Dockerfile.insecure
├── Dockerfile.hardened
├── .dockerignore
├── .gitignore
├── scripts/summarize_trivy.py
├── tests/test_app.py
├── REPORT_NOTES.md
└── README.md
```

## 3. Sukurk ir parodyk nesaugų image

```bash
sudo docker build -f Dockerfile.insecure -t vejo-lab:insecure .
sudo docker run -d --name vejo-insecure -p 127.0.0.1:8001:8000 vejo-lab:insecure
curl -fsS http://127.0.0.1:8001/health
```

Atidaryk `http://127.0.0.1:8001` naršyklėje. Jeigu puslapis rodomas, nufotografuok jį kartu su terminalu, kuriame matyti `docker ps`.

**Įrodymas E02:** nesaugaus Dockerfile turinys (visos eilutės).  
**Įrodymas E03:** sėkmingas `docker build`, veikiantis portalas ir `docker ps`.

Nesaugaus varianto klaidos: sena bazė, `root`, netikras raktas `ENV`, nereikalingi paketai, `ADD .`, perteklinis `EXPOSE 22`, kūrimo serveris. Šis raktas **nėra tikras** ir niekam nesuteikia prieigos.

## 4. Nuskenuok nesaugų image su Trivy

```bash
mkdir -p evidence
sudo trivy image --scanners vuln --format json --output evidence/trivy-insecure.json vejo-lab:insecure
sudo trivy image --scanners vuln --severity CRITICAL,HIGH,MEDIUM,LOW vejo-lab:insecure | tee evidence/trivy-insecure.txt
```

Pirmas Trivy paleidimas gali užtrukti, nes atsisiunčiama pažeidžiamumų duomenų bazė.

Patogiai ištrauk konkrečius CVE:

```bash
jq -r '.Results[]?.Vulnerabilities[]? | [.VulnerabilityID,.PkgName,.InstalledVersion,.FixedVersion,.Severity] | @tsv' evidence/trivy-insecure.json | head -n 25
```

**Įrodymas E04:** Trivy santrauka su rastų pažeidžiamumų skaičiumi pagal Critical / High / Medium / Low.  
**Įrodymas E05:** bent 3 realūs CVE su paketo pavadinimu, versija, pažeidžiamumo informacija ir aptarimu, ar programos kodas pasiekia paveiktą funkcionalumą.

Jei Trivy neranda 3 skirtingų CVE, neišgalvok jų — turėsime koreguoti pasirinktą nesaugų image ir pakartoti skenavimą.

## 5. Sukurk sustiprintą image

```bash
sudo docker build -f Dockerfile.hardened -t vejo-lab:hardened .
```

Paleisk su papildomais apribojimais:

```bash
sudo docker run -d \
  --name vejo-hardened \
  -p 127.0.0.1:8000:8000 \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges:true \
  --memory=256m \
  --cpus=0.5 \
  --pids-limit=64 \
  vejo-lab:hardened
```

Patikrink veikimą:

```bash
curl -fsS http://127.0.0.1:8000/health
sudo docker ps
```

Palauk maždaug 30–45 sekundes ir patikrink būseną:

```bash
sudo docker inspect vejo-hardened --format '{{json .State.Health}}'
```

Jei rodo `unhealthy`, prieš tęsiant reikia patikrinti `sudo docker logs vejo-hardened`.

**Įrodymas E06:** `Dockerfile.hardened`, veikiančio portalo ekrano nuotrauka ir `healthy` būsena.

Patikrink apribojimus:

```bash
sudo docker inspect vejo-hardened --format 'ReadOnly={{.HostConfig.ReadonlyRootfs}} CapDrop={{json .HostConfig.CapDrop}} SecurityOpt={{json .HostConfig.SecurityOpt}} MemoryBytes={{.HostConfig.Memory}} NanoCPUs={{.HostConfig.NanoCpus}} User={{.Config.User}}'
```

**Įrodymas E07:** ši tikra `docker inspect` išvestis. Turėtų matytis `true`, `ALL`, `no-new-privileges:true`, `268435456` atminties limitas, `500000000` CPU kvota nanosekundėmis ir naudotojas `10001:10001`.

## 6. Pakartok skenavimą ir palygink

```bash
sudo trivy image --scanners vuln --format json --output evidence/trivy-hardened.json vejo-lab:hardened
sudo trivy image --scanners vuln --severity CRITICAL,HIGH,MEDIUM,LOW vejo-lab:hardened | tee evidence/trivy-hardened.txt
python scripts/summarize_trivy.py evidence/trivy-insecure.json evidence/trivy-hardened.json
sudo docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}'
sudo docker image inspect vejo-lab:insecure --format '{{json .Config.Env}}'
sudo docker image inspect vejo-lab:hardened --format '{{json .Config.Env}}'
```

**Įrodymas E08:** skenavimas po pataisymų.  
**Įrodymas E09:** prieš / po lentelė, image dydžiai, naudotojas, ENV, CVE skaičius.

`ENV` sąraše gali būti įprastų Python ar sistemos kintamųjų. Svarbu, kad sustiprintame image nebūtų mūsų `DEMO_API_KEY`. Vien tai neįrodo, kad paslapčių kitur tikrai nėra, todėl galime papildomai skenuoti su `trivy image --scanners secret`.

## 7. Įkelk tik sustiprintą image į DockerHub

Šį žingsnį atlik tik kai rezultatai patikrinti. DockerHub svetainėje susikurk **viešą** repozitoriją `vejoenergija-portal`. Tada terminale:

```bash
sudo docker login -u TAVO_DOCKERHUB_VARDAS
sudo docker tag vejo-lab:hardened TAVO_DOCKERHUB_VARDAS/vejoenergija-portal:1.0.0
sudo docker push TAVO_DOCKERHUB_VARDAS/vejoenergija-portal:1.0.0
```

**Įrodymas E10:** sėkmingas `docker push` ir DockerHub viešo repozitorijos puslapio nuoroda. Nerodyk prisijungimo slaptažodžių ar tokenų ekrano nuotraukose. `vejo-lab:insecure` image **nekelk** į DockerHub.

## 8. Užbaik ataskaitą

Pildyk `REPORT_NOTES.md` — ten paruoštos analizės lentelės, kurioms reikia tikrų rezultatų. Į galutinį Word failą perkelsime išvadas, nuotraukas, failų turinį ir DockerHub nuorodą.

Baigęs gali sustabdyti ir pašalinti tik šiuos du laikinus laboratorijos konteinerius:

```bash
sudo docker rm -f vejo-insecure vejo-hardened
```

Tai **nepašalina** image ar tavo kodo failų.

## Dažnos problemos

- `docker: command not found` — Docker neįdiegtas.
- `Cannot connect to the Docker daemon` — patikrink `sudo systemctl status docker` ir bandyk `sudo docker info`.
- `permission denied /var/run/docker.sock` — naudok `sudo docker`, nenustatinėk `chmod 666` Docker socket failui.
- `port is already allocated` — prievadą naudoja kita programa; parodyk klaidą prieš keisdamas komandą.
- `unhealthy` — tikrink `sudo docker logs vejo-hardened`.
- `trivy: command not found` — įdiek `trivy` per `pacman`.

## Oficialios nuorodos

- ArchWiki Docker: https://wiki.archlinux.org/title/Docker
- Docker `run`: https://docs.docker.com/engine/containers/run/
- Trivy image: https://trivy.dev/docs/latest/guide/target/container_image/
- Oficialus Python image: https://hub.docker.com/_/python
