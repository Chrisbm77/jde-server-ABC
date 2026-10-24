# Localizations — Guide Index

Master index page (always re-check for current links): https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/guides.html

## How localizations work (common across every country — read this first)

Every country-specific guide sits on top of the same mechanism, described identically in each guide's introduction chapter:

- **Country server technology.** Country-specific behavior (e.g. validating a tax ID in a format a given country requires, or capturing extra supplier fields) is isolated from the base software as a separate localized program. During normal transaction processing, the system's "country server" decides whether to route into that localized program instead of (or in addition to) the base one.
- **Localization country codes (UDC 00/LC).** Two- and three-digit codes identifying which country's rules apply. Set on user display preferences so the country server knows which localized programs to invoke for that user/session — this is the switch that turns country-specific behavior on.
- **User display preferences** also carry other per-country defaults: date format (e.g. DDMMYY for typical European display) and a language override on top of the base language.
- **Localization setup is additive, not a replacement.** You must still complete the base-module setup (e.g. base Accounts Payable setup) *and* the country-specific setup described in the localization guide — the localization guide never stands alone. This is why a country-specific question almost always needs both a topic `ba-localizations` guide and the relevant base-module guide (topic `ba-financials`, topic `ba-supply-chain-manufacturing`, etc.) fetched together.
- Some countries have deeper, genuinely distinct functionality (e.g. Japan's Wareki date format, Kagami statements, and Hankin Hante payment/draft splitting; Brazil's fiscal notes; Italy's electronic invoicing) — those go well beyond "validate a tax ID" and are worth reading in full rather than assuming the common pattern covers everything.

**Workflow for any country-specific question:** identify the country → find its guide below (or re-fetch the master index if a country isn't listed here) → fetch that guide's introduction chapter for the country-server/UDC setup, then `web_search` for the specific topic (e.g. `"Localizations for India Implementation Guide" GST`) to jump straight to the relevant page → also pull in the base-module guide for the underlying process being localized.

## Country and topic guides (verified against the current master index)

| Country / Topic | HTML | PDF |
|---|---|---|
| Common Features for Localizations | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoacl/index.html | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoacl/common-features-for-localizations-implementation-guide.pdf |
| Australia and Singapore | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoaal/index.html | .../eoaal/localizations-for-australia-and-singapore-implementation-guide.pdf |
| China | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoach/index.html | .../eoach/localizations-for-china-implementation-guide.pdf |
| India | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoaid/index.html | .../eoaid/localizations-for-india-implementation-guide.pdf |
| Japan | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoajp/index.html | .../eoajp/localizations-for-japan-implementation-guide.pdf |
| South Korea | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoask/index.html | .../eoask/localizations-for-south-korea.pdf |
| Taiwan | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoatw/index.html | .../eoatw/localizations-for-taiwan-implementation-guide.pdf |
| BIP Payment Formats for Localizations | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoabi/index.html | .../eoabi/bip-payment-formats-for-localizations-implementation-guide.pdf |
| Common Global Implementation (ISO20022) | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoaci/index.html | .../eoaci/common-global-implementation-iso20022-localizations-implementation-guide.pdf |
| Austria | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoaat/index.html | .../eoaat/localizations-for-austria-implementation-guide.pdf |
| Belgium | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoabl/index.html | .../eoabl/localizations-for-belgium-implementation-guide.pdf |
| Denmark | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoadk/index.html | .../eoadk/localizations-for-denmark-implementation-guide.pdf |
| European Reporting and SEPA Processing | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoael/index.html | .../eoael/localizations-for-european-reporting-and-sepa-processing-implementation-guide.pdf |
| European Union Electronic Invoice Processing | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoaei/index.html | .../eoaei/localizations-for-european-union-electronic-invoice-processing-implementation-guide.pdf |
| Finland | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoafn/index.html | .../eoafn/localizations-for-finland-implementation-guide.pdf |
| France | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoafr/index.html | .../eoafr/localizations-for-france-implementation-guide.pdf |
| Germany | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoadu/index.html | .../eoadu/localizations-for-germany-implementation-guide.pdf |
| Hungary | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoahu/index.html | .../eoahu/localizations-for-hungary-implementation-guide.pdf |
| Italy | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoait/index.html | .../eoait/localizations-for-italy-implementation-guide.pdf |
| Norway | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoano/index.html | .../eoano/localizations-for-norway-implementation-guide.pdf |
| Poland | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoapl/index.html | .../eoapl/localizations-for-poland-implementation-guide.pdf |
| Portugal | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoapt/index.html | .../eoapt/localizations-for-portugal-implementation-guide.pdf |
| Russia | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoaru/index.html | .../eoaru/localizations-for-russia-implementation-guide.pdf |
| Spain | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoasp/index.html | .../eoasp/localizations-for-spain-implementation-guide.pdf |
| Sweden | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoasd/index.html | .../eoasd/localizations-for-sweden-implementation-guide.pdf |
| Switzerland | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoasw/index.html | .../eoasw/localizations-for-switzerland-implementation-guide.pdf |
| Czech Republic | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoacz/index.html | .../eoacz/localizations-for-the-czech-republic-implementation-guide.pdf |
| Netherlands | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoant/index.html | .../eoant/localizations-for-the-netherlands-implementation-guide.pdf |
| United Kingdom and Ireland | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoauk/index.html | .../eoauk/localizations-for-the-united-kingdom-and-ireland-implementation-guide.pdf |
| OECD SAF-T (Standard Audit File for Tax) | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoast/index.html | .../eoast/oecd-standard-audit-file-for-tax-purposes-saf-t-localizations-implementation-guide.pdf |
| Argentina | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoaag/index.html | .../eoaag/localizations-for-argentina-implementation-guide.pdf |
| Brazil | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoabz/index.html | .../eoabz/localizations-for-brazil-implementation-guide.pdf |
| Chile | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoacp/index.html | .../eoacp/localizations-for-chile-implementation-guide.pdf |
| Colombia | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoacs/index.html | .../eoacs/localizations-for-colombia-implementation-guide.pdf |
| Ecuador | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoaed/index.html | .../eoaed/localizations-for-ecuador-implementation-guide.pdf |
| Mexico | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoamx/index.html | .../eoamx/localizations-for-mexico-implementation-guide.pdf |
| Peru | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoape/index.html | .../eoape/localizations-for-peru-implementation-guide.pdf |
| Venezuela | https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/eoavz/index.html | .../eoavz/localizations-for-venezuela-implementation-guide.pdf |

(PDF paths above omit the `https://docs.oracle.com/en/applications/jd-edwards/localizations/9.2/<code>` prefix shown in the HTML column — combine them, or just fetch the HTML index link and follow the PDF link found there.)

Localizations build on top of base functionality — a country question about, say, withholding tax on AP payments will also need the base **Accounts Payable Implementation Guide** (topic `ba-financials`) alongside the country-specific guide. Also frequently relevant: **Address Book** and **Foundation Guide** (topic `ba-cross-product-tools`) for the underlying country-constants (F0070) and address-format setup every localization depends on.
