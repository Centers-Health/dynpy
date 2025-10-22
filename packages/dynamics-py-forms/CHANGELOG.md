# Changelog

<!--next-version-placeholder-->

## v10.0.3 (2025-10-22)
### Fix
- Bug causing groupaware filter to fail on post requests ([`ecd1c9c`](https://github.com/Centers-health/dynpy/commit/ecd1c9cbed49fc445c447a010992c43c85a13348))
- Add tests for groupaware field and widget ([`86a231a`](https://github.com/Centers-health/dynpy/commit/86a231ade35c343fc99a67c6366e489ba65edd08))


## v10.0.2 (2025-10-20)
### Fix
- Incorrect logic for handling data being a dict in groupaware widget ([`c13a884`](https://github.com/Centers-health/dynpy/commit/c13a88466f4f7ba78f254a0e9931bf327e26a79d))


## v10.0.1 (2025-10-20)
### Fix
- Handle missing request/querydict for testing with groupaware ([`59a12c1`](https://github.com/Centers-health/dynpy/commit/59a12c10160ef1c1c2c6475d30e72424972a9d37))


## v10.0.0 (2025-10-16)
### Breaking
- Add group-level filtering support and refactor js into modular widgets ([`2d14c2c`](https://github.com/Centers-health/dynpy/commit/2d14c2c0a28b80596290434236d92e104f7c2aa8))
### Fix
- Ensure jquery.formset js can load html with inline modules ([`39eefb4`](https://github.com/Centers-health/dynpy/commit/39eefb4b41c13edcdda883843aaa0e7e80eac768))


## v9.5.1 (2025-09-10)
### Fix
- Fix bootstrap error styles for range widgets ([`fb244bc`](https://github.com/Centers-health/dynpy/commit/fb244bcfacb1f4d66a08f4f36d60a1d83a9c6962))
- Clearable input style ([`9a6aba4`](https://github.com/Centers-health/dynpy/commit/9a6aba43e96ad8a7d37c0a36bd311981209232be))


## v9.4.0 (2025-09-09)
### Feature
- Update range filter styling ([`cf7d2e4`](https://github.com/Centers-health/dynpy/commit/cf7d2e4e944cfe22d150094b1c91d6f4193d7e63))


## v9.0.0 (2025-08-19)
### Breaking
- Upgrade strawberry-graphql ([`3173106`](https://github.com/Centers-health/dynpy/commit/3173106a074a6ad5c77ec14d991b2ce2061c0f55))


## v7.9.0 (2025-08-08)
### Feature
- Add render_with_context tag ([`1e5fa69`](https://github.com/Centers-health/dynpy/commit/1e5fa69373aaf0016990a85c6fb0cc5bda036096))


## v7.6.0 (2025-07-08)
### Feature
- Add field mixin for ignoring invalid values in choice fields ([`56c4abf`](https://github.com/Centers-health/dynpy/commit/56c4abf693066e75314ecb74dab0bc374b38b6b2))


## v7.4.3 (2025-06-25)
### Fix
- Update readme to remove dm reference ([`1050d8c`](https://github.com/Centers-health/dynpy/commit/1050d8cf8ca06501fa26df5f6642961cd8dd7d84))


## v7.4.2 (2025-06-24)
### Fix
- Change default option rendering for bootstrap select widget ([`2211f5f`](https://github.com/Centers-health/dynpy/commit/2211f5f5d0b3e8673d2a9598273fdc90ffb5c990))


## v7.4.1 (2025-06-19)
### Fix
- Apply updates to submit filter button ([`ee56d63`](https://github.com/Centers-health/dynpy/commit/ee56d635245ece62120a39b3308583a60e40c17f))


## v7.4.0 (2025-06-11)
### Feature
- Update date filters to opt-in for the clear button ([`3c91998`](https://github.com/Centers-health/dynpy/commit/3c91998e5985471bb77a6c2444d5ca4984f64a13))


## v7.3.0 (2025-05-19)
### Feature
- Add clear button for date filters to improve usability ([`0f37b74`](https://github.com/Centers-health/dynpy/commit/0f37b74fa7bbf9b35c833ff0e2506ff9efe4c784))


## v7.2.0 (2025-05-02)
### Feature
- Add inlinemonthrangelastday to include last day in month ([`ad62875`](https://github.com/Centers-health/dynpy/commit/ad6287539910640618b786fade19b6b4c9a8270a))


## v7.1.4 (2025-03-26)
### Other
- Bump package lock files ([`1d5932b`](https://github.com/Centers-health/dynpy/commit/1d5932bc612fc8942552263e97a05a31781f9f55))


## v7.1.3 (2025-02-26)
### Fix
- Monthpicker only working for fields called 'start_date' or 'end_date' ([`e905603`](https://github.com/Centers-health/dynpy/commit/e9056034be2fd23498efb55d9c8010ab1b2592f1))

## v7.1.2 (2025-02-26)
### Fix
- Make sure errors in the date range widget bubble up from subwidgets ([`71b6d0f`](https://github.com/Centers-health/dynpy/commit/71b6d0f9aa4bc14b2f29e1d7b7eec439eaa74f06))

## v7.1.1 (2025-02-19)
### Fix
- Add hx-reswap of innerhtml for hxconfirmmixin ([`fe54e16`](https://github.com/Centers-health/dynpy/commit/fe54e16a02c48bc55a186ac838ede2c4c7676000))

## v7.1.0 (2025-02-19)
### Feature
- Add dynpy_forms ([`5593c9e`](https://github.com/Centers-health/dynpy/commit/5593c9e9ae97bdb4b0903f59d8e0f479eca21fd4))
### Other
- Lint / format ([`6098f71`](https://github.com/Centers-health/dynpy/commit/6098f714a5af46f3494d17153ce1ea5229df3d7d))
- Biome lint ([`5d61cb6`](https://github.com/Centers-health/dynpy/commit/5d61cb6e2b91fe8ab96e0a641557f21cc04a7375))

## v7.0.0 (2025-02-10)
### Fix
* Bump dynpy version to 19.0.0 ([`91b7dfc`](https://github.com/Centers-Health/dynamics-py-forms/commit/91b7dfc66dea6bd482a49781be23f61f90ab98ae))
### Breaking
* bump dynpy version to 19.0.0 ([`91b7dfc`](https://github.com/Centers-Health/dynamics-py-forms/commit/91b7dfc66dea6bd482a49781be23f61f90ab98ae))

## v6.1.0 (2024-12-25)
### Feature
* Update dynpy-core version ([`3affa19`](https://github.com/Centers-Health/dynamics-py-forms/commit/3affa19a8e88949e9afcec9c3811fe18c11a6ca1))

## v6.0.0 (2024-09-30)
### Fix
* Upgrade dynpy core dependency ([`eb44ae9`](https://github.com/Centers-Health/dynamics-py-forms/commit/eb44ae97a3358fed1c93315a7fe1aef51913a1af))
### Breaking
* upgrade dynpy core dependency ([`eb44ae9`](https://github.com/Centers-Health/dynamics-py-forms/commit/eb44ae97a3358fed1c93315a7fe1aef51913a1af))

## v5.3.0 (2024-09-26)
### Feature
* Allow adding addition widget attributes to date range picker ([`6f34bc4`](https://github.com/Centers-Health/dynamics-py-forms/commit/6f34bc46c5eab55ef1c0fd7b4cba8558fa741e90))

## v5.2.0 (2024-09-18)
### Feature
* Change phone number help text to placeholder ([`711b41d`](https://github.com/Centers-Health/dynamics-py-forms/commit/711b41dffdc49c4ef4ba92af52b525b3ccbecb87))
### Fix
* Overriding oredering when with group by field ([`985a548`](https://github.com/Centers-Health/dynamics-py-forms/commit/985a548da4e40527f22d6a51932b83f41c325ea4))

## v5.1.4 (2024-09-18)
### Fix
* Formest not fully rendered on initialization ([`25547f3`](https://github.com/Centers-Health/dynamics-py-forms/commit/25547f32bee31aa99c6df5e6af40b6599240662e))

## v5.1.3 (2024-09-17)
### Fix
* Jquery formset js ([`765ed82`](https://github.com/Centers-Health/dynamics-py-forms/commit/765ed820947ab32b4ed3c846be13fe66be54f8ac))

## v5.1.2 (2024-09-17)
### Fix
* Fix nested formset by scoping the js based on unique id ([`638e9fc`](https://github.com/Centers-Health/dynamics-py-forms/commit/638e9fc2dea544f6987dd9fb4fdbe08252b415c5))

## v5.1.1 (2024-09-13)
### Fix
* Sort by group_by_field ([`57445d0`](https://github.com/Centers-Health/dynamics-py-forms/commit/57445d0f4aba48ea9f2f8e920c03f7dff98fd3f0))

## v5.1.0 (2024-09-13)
### Feature
* Add abstraction layer to grouped model choice field ([`b45426f`](https://github.com/Centers-Health/dynamics-py-forms/commit/b45426fecf800bb29cef5d047735961dad680ee1))

## v5.0.0 (2024-09-03)
### Feature
* Upgrade Django to v4.2.x ([`e02c254`](https://github.com/Centers-Health/dynamics-py-forms/commit/e02c254897221bbb97da386b9650343609b2d415))
### Breaking
* Upgrade Django to v4.2.x ([`e02c254`](https://github.com/Centers-Health/dynamics-py-forms/commit/e02c254897221bbb97da386b9650343609b2d415))

## v4.10.1 (2024-08-30)
### Fix
* Remove needs_confirmation method from HXConfirmMixin ([`3061fce`](https://github.com/Centers-Health/dynamics-py-forms/commit/3061fce6215b2ccfe84740a313e17751d7cf2f50))

## v4.10.0 (2024-08-23)
### Feature
* Raise not implemented exception if confirmation message not set ([`738c1e2`](https://github.com/Centers-Health/dynamics-py-forms/commit/738c1e230980bd3cc1f98cdd401d42b4b5332a9a))
* Make dynamic confirmation usable for hx_requests ([`9615429`](https://github.com/Centers-Health/dynamics-py-forms/commit/9615429f5647249d39c5c56583b3730c7d07ef7d))

## v4.9.0 (2024-08-20)
### Feature
* Add FullObjectGroupedModelChoiceField ([`bdfd089`](https://github.com/Centers-Health/dynamics-py-forms/commit/bdfd089ce444779dba6d312da832f63d20d96a69))

## v4.8.0 (2024-07-19)
### Feature
* Add js block in confirmation ([`024449b`](https://github.com/Centers-Health/dynamics-py-forms/commit/024449bc2f6298781ae9637b7ae5bcea9d2bbffe))

## v4.7.0 (2024-07-19)
### Feature
* Add dynamic confirm view mixin ([`5d56a9b`](https://github.com/Centers-Health/dynamics-py-forms/commit/5d56a9bfa5f8d6b38868225037b3b2cf2d553a7e))

## v4.6.0 (2024-06-03)
### Feature
* Add new formset option: remove_last_add_form_unless_is_only_form ([`f89a3e4`](https://github.com/Centers-Health/dynamics-py-forms/commit/f89a3e4d7b6750bbc16a6c8a49edd7a23722f01d))
### Fix
* Fix js for toggling delete buttons in formsets ([`3b122d9`](https://github.com/Centers-Health/dynamics-py-forms/commit/3b122d9bb70287d64786ac2dd3fddcb4cd171704))

## v4.5.2 (2024-05-21)
### Fix
* Update dynpy core to 15.0.0 ([`b7033d3`](https://github.com/Centers-Health/dynamics-py-forms/commit/b7033d3c6cbaf5c882d61c88c304f523e1a42a42))

## v4.5.1 (2024-04-17)
### Fix
* Set related form instance from initial ([`db90edc`](https://github.com/Centers-Health/dynamics-py-forms/commit/db90edc54dfc9ad30df33ec423cde3df2deb15c9))

## v4.5.0 (2024-04-07)
### Feature
* Update get_form to not use get ([`e75b31b`](https://github.com/Centers-Health/dynamics-py-forms/commit/e75b31b244585728c30635aa928c485cbad46fed))
* Make related form required if fk field is required and is not in the form ([`9b4d2d1`](https://github.com/Centers-Health/dynamics-py-forms/commit/9b4d2d1c68a3ed1bb9a72b9e0399f20111c30a74))
* Move custom error to fk field ([`81d43c6`](https://github.com/Centers-Health/dynamics-py-forms/commit/81d43c61f76e9faa67df5d9a97bb2267e55217a8))
* Rename formset factory functions ([`b5a5886`](https://github.com/Centers-Health/dynamics-py-forms/commit/b5a58864ec3de7a04d081d2423a6be94322d8368))
* Add use unique instance feature ([`563ca11`](https://github.com/Centers-Health/dynamics-py-forms/commit/563ca113109e867519e1318cdd1ca6a142168e4c))
* Allow formset list and associated kwargs list for a single relationship ([`2b5882d`](https://github.com/Centers-Health/dynamics-py-forms/commit/2b5882d369537c236bd6b641565798e8d0e48703))
* Add form error if required field and related form are empty ([`79a7f52`](https://github.com/Centers-Health/dynamics-py-forms/commit/79a7f52c889b4ca86c5b66041412af6bbb40cecc))
* Add multi related model form class ([`28c62e1`](https://github.com/Centers-Health/dynamics-py-forms/commit/28c62e10a866a68c2e48f681f62fda838acb6083))
* Add dyn inline formset classes ([`8990d8c`](https://github.com/Centers-Health/dynamics-py-forms/commit/8990d8c50fca1498acead7d6cf64526cfdf27514))
### Fix
* Fix phone number field class kwargs ([`6a89f18`](https://github.com/Centers-Health/dynamics-py-forms/commit/6a89f18110955bed3b974154ec1f9bee29f84277))
### Documentation
* Update comments for get unique instance methods ([`f030e17`](https://github.com/Centers-Health/dynamics-py-forms/commit/f030e17ebb9252c516673cd718782c12c22efa68))

## v4.4.0 (2024-03-12)
### Feature
* Add django-widget-tweaks code for field rendering ([`2117f8d`](https://github.com/Centers-Health/dynamics-py-forms/commit/2117f8d3ca0c98bcfe057f68c0c2ee10dc745fca))

## v4.3.1 (2024-02-09)
### Fix
* Formset jquery ([`58b69bb`](https://github.com/Centers-Health/dynamics-py-forms/commit/58b69bb70e7c7919d78b817a1bbe9b3736d09838))

## v4.3.0 (2024-02-06)
### Feature
* Copy over field values from keep_field_values based on latest changes ([`f2a5592`](https://github.com/Centers-Health/dynamics-py-forms/commit/f2a5592fb725e01954caa74cba20d87764b0d394))

## v4.2.0 (2024-01-29)
### Feature
* Expose max/min num options in dyn_formset_factory ([`c741405`](https://github.com/Centers-Health/dynamics-py-forms/commit/c74140584e1723f1a2be387647654af65ae5a795))

## v4.1.0 (2024-01-19)
### Feature
* Allow blank option  in TypeAheadModelChoiceField ([`cc0a52f`](https://github.com/Centers-Health/dynamics-py-forms/commit/cc0a52f31e0e360910f8fe24cbf0351479f131bc))

## v4.0.0 (2023-12-13)
### Feature
* Upgrade python 3.8 ~> 3.11 ([`ef54056`](https://github.com/Centers-Health/dynamics-py-forms/commit/ef54056704c8b194531827a15063ab3cbafaf774))
### Breaking
* upgrade python 3.8 ~> 3.11 ([`ef54056`](https://github.com/Centers-Health/dynamics-py-forms/commit/ef54056704c8b194531827a15063ab3cbafaf774))

## v3.8.0 (2023-12-13)
### Feature
* Pin python-semantic-release at 7.31.2 ([`f60e69a`](https://github.com/Centers-Health/dynamics-py-forms/commit/f60e69a7eddade65f2d40e69869b3a16d088926d))
* Update dynpy version (13.0.0) ([`e6a5dff`](https://github.com/Centers-Health/dynamics-py-forms/commit/e6a5dfff6e4bb0ee0670a3c31cdb4a25195c96f4))

## v3.7.0 (2023-12-12)
### Feature
* Upgrade dynpy compatibility (>=8.0.0,<11.0.0) ([`419085b`](https://github.com/Centers-Health/dynamics-py-forms/commit/419085b88813f36e3efb1c0232c3c96edc2203ae))

## v3.6.0 (2023-11-29)
### Feature
* Upgrade dynpy compatibility (>=8.0.0,<10.0.0) ([`0d2149b`](https://github.com/Centers-Health/dynamics-py-forms/commit/0d2149b5d2f2d171d02b26525690244f2c5693be))

## v3.5.0 (2023-10-18)
### Feature
* Update dynpy to version 8.0.0 ([`f22eaf6`](https://github.com/Centers-Health/dynamics-py-forms/commit/f22eaf63b33319a3a32e27428c7c617b92ccc1c1))

## v3.4.0 (2023-09-13)
### Feature
* Update dynpy to 7.1.0 ([`6895d3d`](https://github.com/Centers-Health/dynamics-py-forms/commit/6895d3d1ee8609d4dfa7175126af1b3143151efa))

## v3.3.0 (2023-09-06)
### Feature
* Upgrade dynpy compatibility (>=4.2.0,<7.0.0) ([`b85c329`](https://github.com/Centers-Health/dynamics-py-forms/commit/b85c3295d26425fc20b2736a2a878bec99e8e8f6))

## v3.2.0 (2023-08-04)
### Feature
* Set default item name to model verbose name plural for model choices ([`4f6fec5`](https://github.com/Centers-Health/dynamics-py-forms/commit/4f6fec536527cdece39ed976ded76d3bed431869))
* Option to override default item item_name ([`7df9e04`](https://github.com/Centers-Health/dynamics-py-forms/commit/7df9e04bd18d21359300b9533c0ae6955156f06d))

## v3.1.2 (2023-06-01)
### Fix
* Remove title from selectpicker ([`4656382`](https://github.com/Centers-Health/dynamics-py-forms/commit/46563820814a305724335caa23beae87934dfc51))

## v3.1.1 (2023-05-30)
### Fix
* Fix tooltip on muliselect widget ([`b4a57a6`](https://github.com/Centers-Health/dynamics-py-forms/commit/b4a57a63a3fa826848fef39b1fa4fcca757eb9e3))

## v3.1.0 (2023-05-16)
### Feature
* Add multiple files widget ([`71851a5`](https://github.com/Centers-Health/dynamics-py-forms/commit/71851a5df70e9e700ecce713eafb160617a0e1c2))

## v3.0.1 (2023-05-08)
### Fix
* Fix bug that broke filtering ([`2730441`](https://github.com/Centers-Health/dynamics-py-forms/commit/2730441edcd37f0f91e9a818db28bc6e9c946562))

## v3.0.0 (2023-04-04)
### Fix
* Change formset 'classname' to 'id' ([`caf03f4`](https://github.com/Centers-Health/dynamics-py-forms/commit/caf03f484109050920315c3f75d3aa8b0203ea21))
### Breaking
* Change formset 'classname' to 'id' ([`caf03f4`](https://github.com/Centers-Health/dynamics-py-forms/commit/caf03f484109050920315c3f75d3aa8b0203ea21))

## v2.1.0 (2023-03-23)
### Feature
* Add dynpy 5 compatibility ([`3dce371`](https://github.com/Centers-Health/dynamics-py-forms/commit/3dce371d7f01c1f808012967dd57e10ea0724606))

## v2.0.0 (2023-03-23)
### Fix
* Remove DYNBooleanModelField ([`209df95`](https://github.com/Centers-Health/dynamics-py-forms/commit/209df9515a31c3617cbfae8376b773651139fafe))
### Breaking
* remove DYNBooleanModelField ([`209df95`](https://github.com/Centers-Health/dynamics-py-forms/commit/209df9515a31c3617cbfae8376b773651139fafe))

## v1.0.2 (2023-03-22)
### Fix
* Prevent double deploy from occurring ([`bab3788`](https://github.com/Centers-Health/dynamics-py-forms/commit/bab3788b6537df099236498af21bf63c51ede5b8))

## v1.0.1 (2023-03-21)
### Fix
* Fix id for month picker widget ([`6716ced`](https://github.com/Centers-Health/dynamics-py-forms/commit/6716ceddf373a5312c4c06d179b0eff5bb12d413))

## v1.0.0 (2023-03-16)
### Feature
* Rename generic_formset_factory to dyn_formset_factory ([`4546a60`](https://github.com/Centers-Health/dynamics-py-forms/commit/4546a600f5116dd8c4aa3cde41d20f45dc39015f))
* Change base formset to DynModelFormset ([`cb33a2f`](https://github.com/Centers-Health/dynamics-py-forms/commit/cb33a2f3fc3f05641caad7f2a9da036f3359a59f))
### Breaking
* No such function as generic_formset_factory. It's now named dyn_formset_factory.  ([`4546a60`](https://github.com/Centers-Health/dynamics-py-forms/commit/4546a600f5116dd8c4aa3cde41d20f45dc39015f))
* Formsets used in generic_formset_factory must inherit from DynModelFormset  ([`cb33a2f`](https://github.com/Centers-Health/dynamics-py-forms/commit/cb33a2f3fc3f05641caad7f2a9da036f3359a59f))

## v0.11.0 (2023-03-14)
### Feature
* Add way for formsets to render a header label row ([`9cbbb5e`](https://github.com/Centers-Health/dynamics-py-forms/commit/9cbbb5e37b40c5b8d4b46bc371910b3a8b9a7e64))
* Give option on formset to remove <form> tags ([`d1b34ad`](https://github.com/Centers-Health/dynamics-py-forms/commit/d1b34add162c381c7ebfdabef2b53bbbe402ea65))

## v0.10.5 (2023-03-10)
### Fix
* Run pre-push hooks on ci ([`da6e30d`](https://github.com/Centers-Health/dynamics-py-forms/commit/da6e30da71ac423e5239587b58ee87acb0a334a3))

## v0.10.4 (2023-03-01)
### Fix
* Update dynpy to version 4.0.0 ([`17e7209`](https://github.com/Centers-Health/dynamics-py-forms/commit/17e7209e68ab7b2da60738017f06fab3faa89d1d))

## v0.10.3 (2023-03-01)
### Fix
* Remove last add form feature ([`1dc58bd`](https://github.com/Centers-Health/dynamics-py-forms/commit/1dc58bd9b08f6bfbe3370d36e3656c7a843014c5))

## v0.10.2 (2023-02-24)
### Fix
* Replace hideLastAddForm w/ removeLastAddForm ([`760073a`](https://github.com/Centers-Health/dynamics-py-forms/commit/760073ac547a45a4e0f863719d5d41a7ca03d99a))

## v0.10.1 (2023-02-22)
### Fix
* Set hideLastAddForm to True ([`74b432c`](https://github.com/Centers-Health/dynamics-py-forms/commit/74b432cf5a31aa930fe0993faf9d1dd0e28f24e3))

## v0.10.0 (2023-02-09)
### Feature
* Update formsets ([`a5a6c7b`](https://github.com/Centers-Health/dynamics-py-forms/commit/a5a6c7bd23c901f94ce7c1836daccadde3342a5e))

## v0.9.0 (2023-02-01)
### Feature
* Add ability to select optgroups in the multiselect widget ([`0e67983`](https://github.com/Centers-Health/dynamics-py-forms/commit/0e6798373e9160f8f74aa0000506aaf614f76f04))

## v0.8.0 (2022-12-20)
### Feature
* Add widgets and fields ([`c18f6db`](https://github.com/Centers-Health/dynamics-py-forms/commit/c18f6db4a641b25a05ad486e65f4e4ad5d17a03c))

## v0.7.0 (2022-12-06)
### Feature
* Use dynpy templatetags ([`8209e12`](https://github.com/Centers-Health/dynamics-py-forms/commit/8209e123706ec0542e7cbf06617352d5354dcffd))

## v0.6.0 (2022-11-10)
### Feature
* Add precommit check for migrations ([`4b4d5aa`](https://github.com/Centers-Health/dynamics-py-forms/commit/4b4d5aaeb0fe63306adc77c520e60343d8137dac))

## v0.5.0 (2022-09-14)
### Feature
* Remove 3 .js files ([`9bd1162`](https://github.com/Centers-Health/dynamics-py-forms/commit/9bd1162caf173f61a24e03d9e6aac34a3656e8bb))
### Documentation
* Update installation part of README ([`9f9bc02`](https://github.com/Centers-Health/dynamics-py-forms/commit/9f9bc026538e6e7ee0bbf5bd2a4d3ad4644245a7))

## v0.4.3 (2022-08-30)
### Fix
* CI was removed accidentally ([`424f2a0`](https://github.com/Centers-Health/dynamics-py-forms/commit/424f2a05989b1ce471f65c74c20f342e97c89ab7))

## v0.4.2 (2022-08-23)
### Fix
* Poetry lock update ([`e5c305f`](https://github.com/Centers-Health/dynamics-py-forms/commit/e5c305fd45edef39e6e205245cb16f8f9d227f97))
### Documentation
* Add warning about using python3.10 in venv ([`c5dd5c0`](https://github.com/Centers-Health/dynamics-py-forms/commit/c5dd5c058f3ea30db0d628d47e0f872cc290cee3))
* Add committing section to README ([`c8edfae`](https://github.com/Centers-Health/dynamics-py-forms/commit/c8edfaef158de970508424c59fe0b5aa6af9bf7f))
* Update installation part of README ([`72f5f8b`](https://github.com/Centers-Health/dynamics-py-forms/commit/72f5f8b24ea96659211afe03116f7aaafa70c28a))

## v0.4.1 (2022-08-19)
### Fix
* Include a second poetry build on publish ([`bf72d20`](https://github.com/Centers-Health/dynamics-py-forms/commit/bf72d207b5199ccf47a5e20501a7925aa8c9ed88))

## v0.4.0 (2022-08-19)
### Feature
* Finalize package building and publishing IH ([`ab0aab0`](https://github.com/Centers-Health/dynamics-py-forms/commit/ab0aab0f3187f73395356d9ccd23078fff0383cb))

## v0.3.2 (2022-08-19)
### Fix
* Wrong command parameter ([`22d8288`](https://github.com/Centers-Health/dynamics-py-forms/commit/22d8288604769f70d53ea7bc6ca6c1501ff9d399))
* Poetry publish and changelog ([`155280c`](https://github.com/Centers-Health/dynamics-py-forms/commit/155280c504c6d693b0fb675d522cfb5aae53c217))

## v0.3.1 (2022-08-19)
### Fix
* Install poetry in container ([`f4c741c`](https://github.com/Centers-Health/dynamics-py-forms/commit/f4c741cd5f9ff174620e9c3a8cbc29824bf2970a))

## v0.3.0 (2022-08-19)
### Feature
* Switch to "official" gh action ([`f55413b`](https://github.com/Centers-Health/dynamics-py-forms/commit/f55413b32d2b6611629e8b628b32f5af2ee65160))
### Documentation
* Fix markdown formatting in readme ([`d7e1967`](https://github.com/Centers-Health/dynamics-py-forms/commit/d7e1967144c463c886d11d94f4976afd42beb6c6))
