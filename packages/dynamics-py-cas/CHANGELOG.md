# Changelog

<!--next-version-placeholder-->

## v9.0.0 (2025-08-19)
### Breaking
- Update strawberry_graphql ([`f6baa67`](https://github.com/Centers-health/dynpy/commit/f6baa6708352f92b9aa4747c5c4b70d2bc555dc2))


## v7.0.1 (2025-03-26)
### Other
- Bump package lock files ([`1d5932b`](https://github.com/Centers-health/dynpy/commit/1d5932bc612fc8942552263e97a05a31781f9f55))


## v7.0.0 (2025-02-18)
### Breaking
- Force major version bump ([`6b87c44`](https://github.com/Centers-health/dynpy/commit/6b87c44512623a37f1b9cd4a00b8359f29a19052))

## v6.5.0 (2025-02-18)
### Feature
- Add dynpy-cas package ([`548f3bf`](https://github.com/Centers-health/dynpy/commit/548f3bf253f8865eccc956f54015380be7aad4a4))
### Fix
- Formatting / linting ([`1a39a72`](https://github.com/Centers-health/dynpy/commit/1a39a726ef82efdec045121fc34cbc4a47b12538))
- Update ruff to 0.7.3 ([`fd08264`](https://github.com/Centers-health/dynpy/commit/fd0826476e65b242f6aba8a4f3ba5157723a6203))
- Add biome js ([`b65028e`](https://github.com/Centers-health/dynpy/commit/b65028ea4b38cda8ae80e8c51540d35a87899c88))
- Broken tests ([`8dc6ab5`](https://github.com/Centers-health/dynpy/commit/8dc6ab5264cf38fe4b2df430239ce8e44c48dfb2))
### Other
- Lint ([`072b34b`](https://github.com/Centers-health/dynpy/commit/072b34b0a53befabadc1790e87c7f5e61aa4031d))
- Biome lint ([`567bbbb`](https://github.com/Centers-health/dynpy/commit/567bbbbd4e4d4e5a701b466e0f2e578975cb46ec))

## v6.4.0 (2025-02-03)
### Feature
* Break out ReadOnlyMiddleware.make_form_readonly to allow overriding ([`d5e62d9`](https://github.com/Centers-Health/dynamics-py-cas/commit/d5e62d9a6c73b1f1c02c8c6ab2b2f578ef2be3ad))

## v6.3.0 (2025-01-30)
### Feature
* Break out ReadOnlyMiddleware.user_can_edit to allow overriding ([`357037c`](https://github.com/Centers-Health/dynamics-py-cas/commit/357037cf6997d8e82501eefac71a7fc457089700))

## v6.2.0 (2025-01-06)
### Feature
* Add hmo billing to app codenames for global search ([`dd90d9c`](https://github.com/Centers-Health/dynamics-py-cas/commit/dd90d9c38b1f2b0f2dcabc634b02818dedbea9b2))

## v6.1.0 (2024-12-25)
### Feature
* Update dynpy core verion ([`1061e93`](https://github.com/Centers-Health/dynamics-py-cas/commit/1061e93eabf4a0dded42c8d30b7adfff7c41765d))

## v6.0.1 (2024-10-29)
### Fix
* Fix readonly middleware adding html and tags ([`bfbe2bb`](https://github.com/Centers-Health/dynamics-py-cas/commit/bfbe2bbc51f0a78f8dd084d27a515481056bdd53))

## v6.0.0 (2024-09-30)
### Fix
* Update dynpy core ([`d2976c0`](https://github.com/Centers-Health/dynamics-py-cas/commit/d2976c0c90bfb7520a21c57c494fabaa41bb0a9f))
### Breaking
* update dynpy core ([`d2976c0`](https://github.com/Centers-Health/dynamics-py-cas/commit/d2976c0c90bfb7520a21c57c494fabaa41bb0a9f))

## v5.1.0 (2024-09-30)
### Feature
* Add HMO Billing perm codenames ([`00d0c11`](https://github.com/Centers-Health/dynamics-py-cas/commit/00d0c11595c5c0c4126d89ef2b365f36ae796c8f))

## v5.0.0 (2024-09-03)
### Feature
* Upgrade Django to v4.2.x ([`9e1bb52`](https://github.com/Centers-Health/dynamics-py-cas/commit/9e1bb52ab58f0dcf086bc523ce82e0ea8653d480))
### Breaking
* Upgrade Django to v4.2.x ([`9e1bb52`](https://github.com/Centers-Health/dynamics-py-cas/commit/9e1bb52ab58f0dcf086bc523ce82e0ea8653d480))

## v4.7.1 (2024-06-14)
### Fix
* Fix bug in ReadOnlyMiddleware where broke for not logged in users ([`bfb0096`](https://github.com/Centers-Health/dynamics-py-cas/commit/bfb00964009e1621a8bc832d9f98a7b8722520ee))

## v4.7.0 (2024-06-10)
### Feature
* Bootstrap pats app ([`e5ded6f`](https://github.com/Centers-Health/dynamics-py-cas/commit/e5ded6f8ee4f0270d833b0f3e6f88f0673179168))

## v4.6.2 (2024-06-06)
### Fix
* Fix readonly middleware for hx_requests ([`5044c46`](https://github.com/Centers-Health/dynamics-py-cas/commit/5044c46d6ca704c218a2bb38f8bf73f3ff0071f7))

## v4.6.1 (2024-05-21)
### Fix
* Update dynpy core to 15.0.0 ([`22fb7a0`](https://github.com/Centers-Health/dynamics-py-cas/commit/22fb7a0c8787ddc2d9ed19d1624dcf2fbae449ee))

## v4.6.0 (2024-05-06)
### Feature
* Remove null check for emr resident id (converted to dash in graph query) ([`61edd8b`](https://github.com/Centers-Health/dynamics-py-cas/commit/61edd8b22c9f5c17a903e62b08fcb2fef711ac66))
* Improve responsiveness on resident global search ([`9329e14`](https://github.com/Centers-Health/dynamics-py-cas/commit/9329e1410aa4423ad17b6a405fc36b1dcc17118a))
* Add emr id to global resident search results display ([`5385c75`](https://github.com/Centers-Health/dynamics-py-cas/commit/5385c75ef320ebf5e7e21d4ffa06fa3907995b1d))

## v4.5.0 (2024-05-02)
### Feature
* Add Overtime codename ([`c7852e6`](https://github.com/Centers-Health/dynamics-py-cas/commit/c7852e6ee11a324a6c24cfe003028937e0acecec))

## v4.4.0 (2024-03-27)
### Feature
* Redirect middleware to previous path ([`3e031c4`](https://github.com/Centers-Health/dynamics-py-cas/commit/3e031c498dfe7efb5078812bb791d2498893943d))

## v4.3.0 (2024-02-26)
### Feature
* Update resident-global-search to use appLinks instead of window._jsConfig.apps ([`e44c409`](https://github.com/Centers-Health/dynamics-py-cas/commit/e44c409f5a523aa4f644e0f52eea66bf222692bd))

## v4.2.0 (2024-02-21)
### Feature
* Add SURVEYS to Codename enum ([`b4717ef`](https://github.com/Centers-Health/dynamics-py-cas/commit/b4717ef6b0c418072f0a4eb54cee21c4962c8734))

## v4.1.0 (2024-02-02)
### Feature
* Add user_passes_test decorator ([`0e5abac`](https://github.com/Centers-Health/dynamics-py-cas/commit/0e5abac24acdb681add5a907c64c33da6deb9ff9))

## v4.0.0 (2024-01-02)
### Feature
* Add resident global search from AR ([`10a3af2`](https://github.com/Centers-Health/dynamics-py-cas/commit/10a3af26b2eda76fbe602ba2b9898a5a51cdae34))
### Breaking
* Add resident global search from AR ([`10a3af2`](https://github.com/Centers-Health/dynamics-py-cas/commit/10a3af26b2eda76fbe602ba2b9898a5a51cdae34))

## v3.0.0 (2023-12-13)
### Feature
* Upgrade python 3.8 ~> 3.11 ([`1b3cbc7`](https://github.com/Centers-Health/dynamics-py-cas/commit/1b3cbc74bcdb359057cb99393aa3f482efe051c0))
### Fix
* Pin semantic release + update dynpy ([`40b51be`](https://github.com/Centers-Health/dynamics-py-cas/commit/40b51bec4823fe3df8fc75a86f35b7c4c0ef8091))
### Breaking
* pin semantic release + update dynpy ([`40b51be`](https://github.com/Centers-Health/dynamics-py-cas/commit/40b51bec4823fe3df8fc75a86f35b7c4c0ef8091))
* upgrade python 3.8 ~> 3.11 ([`1b3cbc7`](https://github.com/Centers-Health/dynamics-py-cas/commit/1b3cbc74bcdb359057cb99393aa3f482efe051c0))

## v2.13.0 (2023-12-13)
### Feature
* Update dynpy version (13.0.0) ([`5deb751`](https://github.com/Centers-Health/dynamics-py-cas/commit/5deb751bc1dcde08910347ef39711b079bc70461))

## v2.12.0 (2023-12-12)
### Feature
* Upgrade dynpy compatibility (>=8.0.0,<11.0.0) ([`cb29be5`](https://github.com/Centers-Health/dynamics-py-cas/commit/cb29be5447d2d3910b6df02dcde369ee553fa5bf))

## v2.11.0 (2023-11-29)
### Feature
* Upgrade dynpy compatibility (>=8.0.0,<10.0.0) ([`5b55ac1`](https://github.com/Centers-Health/dynamics-py-cas/commit/5b55ac1dceff6d87b1353fa42bb2c90e946b4d81))

## v2.10.0 (2023-10-18)
### Feature
* Update dynpy to version 8.0.0 ([`444c3d7`](https://github.com/Centers-Health/dynamics-py-cas/commit/444c3d77480dc756ddd06251d278f0d26957fce4))

## v2.9.0 (2023-09-20)
### Feature
* Allow read only urls from settings ([`9c441f2`](https://github.com/Centers-Health/dynamics-py-cas/commit/9c441f29e5616bd77a1196ca72301991e9f874b3))

## v2.8.1 (2023-09-15)
### Fix
* Allow request with no app_name ([`5ae580c`](https://github.com/Centers-Health/dynamics-py-cas/commit/5ae580c3de7d9049671eef7440a9c922db709f3a))

## v2.8.0 (2023-09-13)
### Feature
* Add front-end read only capabilities to middleware ([`0b8355d`](https://github.com/Centers-Health/dynamics-py-cas/commit/0b8355d2eb9793cd1c87108bc96030758fb16995))

## v2.7.0 (2023-09-13)
### Feature
* Upgrade dynpy to 7.1.0 ([`a219298`](https://github.com/Centers-Health/dynamics-py-cas/commit/a219298dd3f37b5de3f8aa1fdad83ecfb2379d24))

## v2.6.0 (2023-09-13)
### Feature
* Add new Codename - LEP_USER ([`1d4127f`](https://github.com/Centers-Health/dynamics-py-cas/commit/1d4127fae30acdd4fcfe501717a525478a662547))

## v2.5.0 (2023-09-11)
### Feature
* Add ReadOnlyMiddleware to restrict edits without editor perms ([`8df758a`](https://github.com/Centers-Health/dynamics-py-cas/commit/8df758a0b5ac218809e996a2a7de70cdd6fe11c4))

## v2.4.0 (2023-09-06)
### Feature
* Upgrade dynpy compatibility (>=5.9.1,<7.0.0) ([`2c41759`](https://github.com/Centers-Health/dynamics-py-cas/commit/2c41759b277877f70f91563904ae54863cdf4062))

## v2.3.0 (2023-08-22)
### Feature
* Add Editor permissions ([`663e6ef`](https://github.com/Centers-Health/dynamics-py-cas/commit/663e6efef16d117547b0217195cb9a9e44fa79c9))

## v2.2.0 (2023-07-31)
### Feature
* Create JWTCookieMiddleware ([`bc60c14`](https://github.com/Centers-Health/dynamics-py-cas/commit/bc60c141cb189427f007058bc5e432aa3a615274))

## v2.1.0 (2023-07-03)
### Feature
* Add OTPRequiredMiddleware and perm ([`c765415`](https://github.com/Centers-Health/dynamics-py-cas/commit/c765415cab79a1fcb444e37dadae229ee3c04ef5))

## v2.0.0 (2023-06-26)
### Feature
* Remove strawberry_django_jwt dependency (rolled into dynpy-core) ([`9849f41`](https://github.com/Centers-Health/dynamics-py-cas/commit/9849f419c6290efd72c22c862530d973ec82bf23))
### Breaking
* Remove strawberry_django_jwt dependency (rolled into dynpy-core) ([`9849f41`](https://github.com/Centers-Health/dynamics-py-cas/commit/9849f419c6290efd72c22c862530d973ec82bf23))

## v1.1.1 (2023-05-29)
### Fix
* Make useless change to trigger version bump for facility config enum change ([`13984a1`](https://github.com/Centers-Health/dynamics-py-cas/commit/13984a1c70dae63a35d61c497ba86a02fec81c1c))

## v1.1.0 (2023-05-22)
### Feature
* Add read-only option for facility config ([`b33d5c1`](https://github.com/Centers-Health/dynamics-py-cas/commit/b33d5c1902cae7fd9285cdf337fe335549e5eefa))

## v1.0.0 (2023-05-15)
### Feature
* Remove redundant permission sync on login ([`2bdcea5`](https://github.com/Centers-Health/dynamics-py-cas/commit/2bdcea5e116dcf2dc96c26af7015e15ea8db9b89))
### Breaking
* Removes permission sync on login. Syncing permissions is now handled by graphql endpoints that CAS calls when the user the permissions are updated  ([`2bdcea5`](https://github.com/Centers-Health/dynamics-py-cas/commit/2bdcea5e116dcf2dc96c26af7015e15ea8db9b89))

## v0.7.0 (2023-05-08)
### Feature
* Handle permissions=None in PermissionSyncer (don't sync) ([`11777d3`](https://github.com/Centers-Health/dynamics-py-cas/commit/11777d35f6b20accdf772da9995951f80eb1a00c))

## v0.6.5 (2023-03-28)
### Fix
* Remove strawberry dependencies ([`201bbdc`](https://github.com/Centers-Health/dynamics-py-cas/commit/201bbdcbd52d1d846ae39b0210fd96eccae0b592))

## v0.6.4 (2023-03-22)
### Fix
* Prevent double deploy from occurring ([`3fb3470`](https://github.com/Centers-Health/dynamics-py-cas/commit/3fb3470a4c903d666641e82a9ddbd915dba6efb7))

## v0.6.3 (2023-03-10)
### Fix
* Run pre-push hooks on ci ([`b3a9b47`](https://github.com/Centers-Health/dynamics-py-cas/commit/b3a9b47b8572f2086c44ffc04d69ee33df35b939))

## v0.6.2 (2023-02-09)
### Fix
* Revert "fix: Add csrf_exempt to logout url" ([#14](https://github.com/Centers-Health/dynamics-py-cas/issues/14)) ([`d349970`](https://github.com/Centers-Health/dynamics-py-cas/commit/d349970ee0e27d31eef8e98f04fd1744ea7ffee8))

## v0.6.1 (2023-02-08)
### Fix
* Add csrf_exempt to logout url ([`0151411`](https://github.com/Centers-Health/dynamics-py-cas/commit/0151411729a80dd28c483f9fcf60de10d1e424d5))

## v0.6.0 (2023-02-08)
### Feature
* Add cas-ng auth urls (login, logout, callback) ([`9ba59db`](https://github.com/Centers-Health/dynamics-py-cas/commit/9ba59db60b7df8cb615f66119caa2e5f3d30f981))

## v0.5.0 (2023-02-02)
### Feature
* Att strawberry django jwt package ([`1e79254`](https://github.com/Centers-Health/dynamics-py-cas/commit/1e792547351c9eaecfbe18ecac65f02f14f7208f))

## v0.4.0 (2023-01-11)
### Feature
* Add codename enum ([`1d8391c`](https://github.com/Centers-Health/dynamics-py-cas/commit/1d8391cf81954c45eff3c62516bac4cc59c415b4))

## v0.3.0 (2022-11-10)
### Feature
* Add precommit check for migrations ([`cdb75a5`](https://github.com/Centers-Health/dynamics-py-cas/commit/cdb75a5b81af7ee157c73707558eba810b54c452))

## v0.2.1 (2022-11-06)
### Fix
* Handle permission name changes ([`e083607`](https://github.com/Centers-Health/dynamics-py-cas/commit/e08360724808b19abaaa0dda258c91bf08ab49c6))

## v0.2.0 (2022-09-23)
### Feature
* Create info_syncer class ([`c1ea9d9`](https://github.com/Centers-Health/dynamics-py-cas/commit/c1ea9d9ec1113d0afa81e2df2235f66db42daf34))
* Add su,staff,email to signal receiver ([`8d32241`](https://github.com/Centers-Health/dynamics-py-cas/commit/8d322416d3d5528c9b678cb599f52affefd80006))

## v0.1.0 (2022-09-14)
### Feature
* Initial Commit ([`a6d0350`](https://github.com/Centers-Health/dynamics-py-cas/commit/a6d03509df9a61fbaab8d18058ab34a501e1245e))
### Documentation
* Update Readme ([`e50d9de`](https://github.com/Centers-Health/dynamics-py-cas/commit/e50d9de3820cd74a9e2ec8f660621ae2143e8236))
