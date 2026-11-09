# Užduotis 3 — saugus CI/CD pipeline

**Autorius:** Mateuš Juchnevič

Šį priedą išarchyvuok **esamo** `vejoenergija-task1` projekto šakniniame aplanke. Jis prideda `.github/workflows/security.yml` ir `ci/` katalogą. **Netrink** esamų failų ar `evidence/` katalogo.

## A. Patikrink, kad naudojama galutinė saugi versija

`Dockerfile.hardened` abiejose `FROM` eilutėse turi būti `python:3.12.16-slim-trixie`. `requirements.txt` turi likti su `Flask==3.1.3` ir `gunicorn==26.2.0`.

## B. Paruošk tyčia nesėkmingą paleidimą

1. Laikinai pakeisk `requirements.txt` turinį pagal `requirements.fail.txt` (trys senos priklausomybės).
2. Nukopijuok `ci/examples/bad_example.py.sample` į projekto šaknį pavadinimu `bad_example.py`. Tai netikra paslaptis ir nesaugus SQL kodo pavyzdys, jo nevykdyk.
3. `git add .`, `git commit -m "Lab: demonstrate failing security checks"` ir `git push`.
4. GitHub → Actions → VejoEnergija Security CI. Išsaugok raudono paleidimo santrauką ir kiekvieno job išvestis.

Numatomas rezultatas: Secrets job FAIL dėl netikro rakto; SCA perspėja dėl senų versijų; SAST rodo SQL konstravimo riziką; Build/SBOM job dėl nesėkmingų saugumo vartų lieka praleistas. Pažeidžiamumo kritiškumo vartai sukonfigūruoti taip, kad tik Critical sustabdo, o kiti radiniai yra informaciniai.

## C. Pataisyk ir parodyk žalią paleidimą

1. Grąžink `requirements.txt`:

   ```text
   Flask==3.1.3
   gunicorn==26.2.0
   ```

2. Pašalink tik laikiną `bad_example.py` iš savo projekto (jokio tikro rakto ten nėra). Pavyzdys `ci/examples/` išlieka dokumentacijai, jo CI neskaito.
3. `git add -A`, `git commit -m "Fix dependency versions and remove demo vulnerabilities"`, `git push`.
4. GitHub Actions paleidimas turi būti žalias, jei atnaujinta vulnerability DB neranda Critical ir neatsiranda aplinkos klaidų.
5. Atsisiųsk artefaktą `vejoenergija-sbom` iš žalo paleidimo. Jame bus `sbom.cdx.json`.

## D. Priklausomybių kilmė SBOM

Numatytos tiesioginės priklausomybės: `Flask` ir `gunicorn` (abu yra `requirements.txt`). Netiesioginės: `Werkzeug`, `Jinja2` (Flask priklausomybės). Būtinai patvirtink šias konkrečias versijas gautame SBOM.

## E. Įrodymai Word failui

- E3-01: `.github/workflows/security.yml` ir šešių jobs sąrašas.
- E3-02: nesėkmingas Actions paleidimas (raudonas) ir Secret job išvestis.
- E3-03: SCA išvestis su pasenusia `Flask`/`Werkzeug` versija ir CVE.
- E3-04: SAST išvestis su SQL įspėjimu (pvz., Bandit B608).
- E3-05: pataisytas kodas, sėkmingas paleidimas (žalias).
- E3-06: atsisiųstas `sbom.cdx.json` ir 2 tiesioginės + 2 netiesioginės priklausomybės.

## F. Paaiškinimai dėstytojui

**Quality gate**: `ci/check_secrets.py` bet kokiam mūsų taisykles atitinkančiam slaptam duomeniui grąžina klaidos kodą 1. Trivy SCA ir image skenavimai su `--severity CRITICAL --exit-code 1` stabdo Critical radinius, o žemesnių lygių rezultatai registruojami, bet nestabdo pipeline.

**Ribotumai**: demo paslapčių skeneris yra siauras, o `pip-audit` ir SAST parodyti kaip informaciniai testai. Tikroje organizacijoje naudotume Gitleaks ar TruffleHog su plačiomis taisyklėmis, architektūrinį taisyklių rinkinį, privalomą code review ir apsaugotus runnerius.

**Atakos tipai**: dependency confusion išnaudoja neteisingą viešų/vidinių paketų šaltinių prioritetą; typosquatting naudoja į tikrų paketų pavadinimus panašius vardus; SolarWinds tipo atakoje kompromituojama teisėta programinės įrangos tiekimo grandinė. Vien CVE skenavimas ne visada aptinka tokias grėsmes.

**Runner sauga**: minimalios workflow teisės (`contents: read`), apsaugotos šakos, review prieš `main`, paslaptys tik per CI secret saugyklą, trumpalaikiai tokenai ir patikrinti/pasirašyti artefaktai. Skenuoti tik išleidimo pabaigoje nepakanka, nes pažeidžiamumai gali patekti į šaltinį daug anksčiau.
