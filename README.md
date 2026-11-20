🌐 **English** · [Deutsch](README.de.md)

# strongt1me PS5 Payloads – source for the Payload Manager

Source (custom repository) for the [PS5 Payload Manager](https://github.com/itsPLK/ps5-payload-manager) by itsPLK.

## Add the source

Payload Manager → **Settings** → **Manage Sources** → **Add Source** → paste this URL:

```
https://raw.githubusercontent.com/strongt1me/ps5-payload-source/main/payloads.json
```

## Included payloads

| Payload | Project |
| :--- | :--- |
| PS5 Cooling & System Center – Pro | [ps5-cooling-system-center-pro](https://github.com/strongt1me/ps5-cooling-system-center-pro) |
| USB Formatter | [ps5-usb-formatierer](https://github.com/strongt1me/ps5-usb-formatierer) |
| PS5 Medic + PS5 Medic Diagnose | [ps5-medic-ui-tool](https://github.com/strongt1me/ps5-medic-ui-tool) |

## Automatic updates

`payloads.json` is built by the GitHub Action [`update-source.yml`](.github/workflows/update-source.yml)
from the `payload-manager.json` files of the individual projects (`build_source.py`):

- **every hour** automatically,
- **manually** via *Actions → Update payload source → Run workflow*,
- **right after a release** (optional, see below).

A commit is only made when something has changed. If a manifest is unreachable or invalid,
the run fails and the previous `payloads.json` stays unchanged.

Adding a new project: add an entry to `MANIFESTS` in `build_source.py` and push.

### Optional: update right after a release

1. Create a fine-grained personal access token: only for this repository, permission **Contents: Read and write**.
2. Store it as the secret `SOURCE_REPO_TOKEN` in each payload repository.
3. Append this step to the end of the release workflow of those payload repositories:

```yaml
      - name: Update payload source
        if: ${{ success() }}
        run: |
          curl -fsS -X POST \
            -H "Authorization: Bearer ${{ secrets.SOURCE_REPO_TOKEN }}" \
            -H "Accept: application/vnd.github+json" \
            https://api.github.com/repos/strongt1me/ps5-payload-source/dispatches \
            -d '{"event_type":"payload-released"}'
```

Without this step a new release reaches the source within an hour at the latest.
