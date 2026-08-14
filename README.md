# allergo-legal

Publiczne dokumenty prawne aplikacji mobilnej **AllerGo** (Android, Google Play).
Repozytorium zawiera wyłącznie statyczny HTML — kod aplikacji jest w osobnym, prywatnym repozytorium.

## Adresy publiczne

| Dokument | URL |
| --- | --- |
| Strona główna | https://bzul85.github.io/allergo-legal/ |
| Privacy Policy (EN) | https://bzul85.github.io/allergo-legal/privacy/ |
| Terms of Use (EN) | https://bzul85.github.io/allergo-legal/terms/ |
| Polityka prywatności (PL) | https://bzul85.github.io/allergo-legal/pl/privacy/ |
| Regulamin (PL) | https://bzul85.github.io/allergo-legal/pl/terms/ |

Adres wymagany przez Google Play Console (pole „Polityka prywatności”):
`https://bzul85.github.io/allergo-legal/privacy/`

## Struktura

```
.
├── index.html            # wybór dokumentu i języka
├── assets/style.css      # wspólne style (light + dark)
├── privacy/index.html    # Privacy Policy (EN)
├── terms/index.html      # Terms of Use (EN)
└── pl/
    ├── privacy/index.html
    └── terms/index.html
```

## Zasady aktualizacji

1. Każdy dokument ma w nagłówku **numer wersji** i **datę wejścia w życie** — zmieniaj oba przy każdej zmianie merytorycznej.
2. Wersje PL i EN muszą pozostać zgodne treściowo. Zmiana w jednym języku wymaga zmiany w drugim w tym samym commicie.
3. **Po każdej zmianie treści przegeneruj asset aplikacji** (patrz niżej) i zaktualizuj stałą `termsVersion` w `lib/main.dart`, aby użytkownicy zostali poproszeni o ponowną akceptację.
4. Zmiana wpływająca na to, jakie dane obsługuje aplikacja, wymaga równoległej aktualizacji formularza **Bezpieczeństwo danych** w Google Play Console.
5. Nie usuwaj istniejących adresów URL — są osadzone w aplikacji i w Play Console.

## Synchronizacja z aplikacją

Aplikacja AllerGo pokazuje **pełną treść obu dokumentów offline**, więc nosi ich kopię jako asset (`assets/legal/legal.json`). Kopia nie jest pobierana z sieci — aplikacja nie wykonuje żadnych własnych połączeń i polityka prywatności to deklaruje.

Po zmianie treści HTML uruchom konwerter:

```bash
python3 tools/build_app_asset.py "/ścieżka/do/AllerGo"
```

Skrypt czyta opublikowane pliki HTML, spłaszcza je do czytelnego tekstu i zapisuje asset w repozytorium aplikacji. Pole `VERSION` w skrypcie musi zgadzać się z wersją w nagłówkach dokumentów.

Zabezpieczenie: test `the asset version matches the Terms version users accept` w `test/widget_test.dart` porównuje `version` z assetu ze stałą `termsVersion`. Jeśli zmienisz jedno, a zapomnisz drugiego, testy aplikacji padają.

Skrypt nie jest częścią builda Fluttera — uruchamiasz go ręcznie, gdy zmienia się treść.

## Hosting

GitHub Pages, gałąź `main`, katalog `/` (root).

## Kontakt

Adrian Kazula — bzul.dev@gmail.com
