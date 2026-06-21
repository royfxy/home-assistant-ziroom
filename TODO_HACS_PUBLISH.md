# HACS Official Directory TODO

Goal: publish `royfxy/home-assistant-ziroom` to the default HACS integration directory.

## 1. Stabilize The Release Branch

- [ ] Merge the token reauthentication fix into the main release branch.
- [ ] Confirm the integration still loads after a Home Assistant restart.
- [ ] Confirm expired tokens trigger Home Assistant reauthentication.
- [ ] Confirm manually updating the token from the integration configuration works.
- [ ] Update `custom_components/ziroom/manifest.json` `version` to the release version.
- [ ] Keep `hacs.json` `homeassistant` minimum version aligned with actual code compatibility.

## 2. Repository Metadata

- [ ] Ensure the GitHub repository is public.
- [ ] Ensure GitHub Issues are enabled.
- [ ] Add a concise GitHub repository description.
- [ ] Add GitHub topics, for example:
  - `home-assistant`
  - `home-assistant-custom-component`
  - `hacs`
  - `ziroom`
  - `smart-home`
- [ ] Confirm README includes install, configuration, supported devices, and token update instructions.
- [ ] Add a HACS "My" link to the README after the repository is ready.

## 3. HACS And Home Assistant Validation

- [x] Add `.github/workflows/hacs.yml` with `hacs/action@main`.
- [x] Set the HACS validation category to `integration`.
- [x] Add a Hassfest workflow for Home Assistant integration validation.
- [ ] Fix all HACS validation failures.
- [ ] Fix all Hassfest validation failures.
- [ ] Confirm both workflows pass on the release branch.

## 4. Brands

- [ ] Prepare brand assets for the `ziroom` domain.
- [ ] Submit a PR to `home-assistant/brands` for `custom_integrations/ziroom`.
- [ ] Wait for the brands PR to merge, or confirm HACS review accepts the current brand state.

## 5. GitHub Release

- [ ] Create a semver tag, for example `v1.0.1`.
- [ ] Publish a GitHub Release for that tag. A tag alone is not enough for HACS release version discovery.
- [ ] Verify HACS can see the released version when the repo is installed as a custom repository.
- [ ] Restart Home Assistant and verify the installed release works.

## 6. Submit To HACS Default

- [ ] Fork `hacs/default`.
- [ ] Create a new branch from `master`.
- [ ] Add `royfxy/home-assistant-ziroom` to the `integration` file in alphabetical order.
- [ ] Open a pull request to `hacs/default`.
- [ ] Fill out the PR template completely and accurately.
- [ ] Keep the PR branch editable by maintainers.
- [ ] Watch automated checks and fix any failures.

## 7. After Acceptance

- [ ] Confirm the repository appears in HACS search without adding a custom repository.
- [ ] Update README to remove or de-emphasize custom repository install steps if desired.
- [ ] Create a normal release process for future updates.
- [ ] Document how to handle token expiry and reauthentication for users.
