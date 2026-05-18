# Cenová poistka pre branislav.website

Tento priečinok obsahuje validačný skript, ktorý porovná HTML stránky
proti jedinému zdroju pravdy `prices.json` v koreni repozitára.
Cieľ: zabrániť, aby sa na web dostali nesprávne ceny.

## Ako to funguje

1. `prices.json` (v koreni) je **jediný zdroj pravdy** pre názvy produktov,
   kategórie, hlavné ceny a varianty (napr. ESET).
2. `scripts/check_prices.py` pri každom behu:
   - skontroluje, že každá samostatná produktová stránka `licencia-*.html`
     obsahuje očakávanú hlavnú cenu a všetky varianty,
   - skontroluje, že katalóg `licencie.html` má pre každý produkt zhodnú cenu,
   - skontroluje, že kategória `antivirus` má aspoň jeden produkt – ak nie,
     vypíše `KRITICKÉ` a zastaví publikáciu.
3. Pri akomkoľvek rozdiele vypíše ľudský report a vráti exit kód `1`.
4. V GitHub Actions (`.github/workflows/deploy.yml`) beží pred SFTP nahraním
   na Hostinger – ak skript zlyhá, **deploy sa nevykoná**.

## Ako aktualizovať cenu (správny postup)

1. Otvor `prices.json` a uprav cenu **iba na jednom mieste** – v zázname
   daného produktu (pole `price`, prípadne `variants[].price`).
2. Uprav cenu v HTML – obvykle treba zmeniť:
   - samostatnú produktovú stránku `licencia-<id>.html`,
   - katalóg `licencie.html` (pole `price:` v poli `PRODUCTS`).
3. Spusti lokálnu kontrolu:
   ```bash
   python3 scripts/check_prices.py
   ```
4. Ak skript píše `✓ Všetky ceny súhlasia` – môžeš commitnúť a pushnúť.
   GitHub Actions to ešte raz overí pred deploy-om.

## Lokálne spustenie

Stačí Python 3 (žiadne závislosti):

```bash
python3 scripts/check_prices.py
```

Voliteľné argumenty:

- `--root <cesta>` – iný koreňový adresár (default `.`)
- `--prices <cesta>` – iný cenník (default `prices.json`)

## Návratové kódy

| Kód | Význam                                              |
|-----|-----------------------------------------------------|
| 0   | Všetko v poriadku, publikácia môže pokračovať.       |
| 1   | Nájdený rozdiel alebo chýbajúca povinná kategória.   |
| 2   | Chyba konfigurácie (napr. nenájdený `prices.json`).  |

## Formát cien

Slovenský formát s čiarkou a medzerou pred eurom: `19,07 €`.
Skript akceptuje aj zápisy s nedeliteľnou medzerou (NBSP / U+202F) a
zápis s desatinnou bodkou v JS objekte (`19.07`), pretože katalóg
`licencie.html` používa tieto formáty v dátach.
