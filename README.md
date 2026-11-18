# strongt1me PS5 Payloads – Quelle für den Payload Manager

Quelle (Custom Repository) für den [PS5 Payload Manager](https://github.com/itsPLK/ps5-payload-manager) von itsPLK.

## Quelle hinzufügen

Payload Manager → **Settings** → **Manage Sources** → **Add Source** → diese URL einfügen:

```
https://raw.githubusercontent.com/strongt1me/ps5-payload-source/main/payloads.json
```

## Enthaltene Payloads

| Payload | Projekt |
| :--- | :--- |
| PS5 Cooling & System Center – Pro | [ps5-cooling-system-center-pro](https://github.com/strongt1me/ps5-cooling-system-center-pro) |
| USB Formatter | [ps5-usb-formatierer](https://github.com/strongt1me/ps5-usb-formatierer) |
| PS5 Medic + PS5 Medic Diagnose | [ps5-medic-ui-tool](https://github.com/strongt1me/ps5-medic-ui-tool) |

## Automatische Aktualisierung

`payloads.json` wird von der GitHub Action [`update-source.yml`](.github/workflows/update-source.yml)
aus den `payload-manager.json`-Dateien der einzelnen Projekte gebaut (`build_source.py`):

- **stündlich** automatisch,
- **manuell** über *Actions → Payload-Quelle aktualisieren → Run workflow*,
- **sofort nach einem Release** (optional, siehe unten).

Committet wird nur, wenn sich etwas geändert hat. Ist ein Manifest nicht erreichbar oder fehlerhaft,
schlägt der Lauf fehl und die bisherige `payloads.json` bleibt unverändert.

Neues Projekt aufnehmen: Eintrag in `MANIFESTS` in `build_source.py` ergänzen und pushen.

### Optional: sofort nach einem Release aktualisieren

1. Fine-grained Personal Access Token erstellen: nur für dieses Repo, Berechtigung **Contents: Read and write**.
2. In jedem Payload-Repo als Secret `SOURCE_REPO_TOKEN` hinterlegen.
3. Am Ende des Release-Workflows dieser Payload-Repos diesen Schritt anhängen:

```yaml
      - name: Payload-Quelle aktualisieren
        if: ${{ success() }}
        run: |
          curl -fsS -X POST \
            -H "Authorization: Bearer ${{ secrets.SOURCE_REPO_TOKEN }}" \
            -H "Accept: application/vnd.github+json" \
            https://api.github.com/repos/strongt1me/ps5-payload-source/dispatches \
            -d '{"event_type":"payload-released"}'
```

Ohne diesen Schritt kommt ein neues Release spätestens nach einer Stunde in der Quelle an.
