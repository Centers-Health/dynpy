# Changelog

<!--next-version-placeholder-->

## v13.2.1 (2025-03-04)
### Fix
- Broken test ([`ece3b94`](https://github.com/Centers-health/dynpy/commit/ece3b943b031cbf6e1978ce4fcaafabfe9ccaba5))


## v13.2.0 (2025-02-20)
### Feature
- Add dynpy_gfl ([`12918e9`](https://github.com/Centers-health/dynpy/commit/12918e9637ee867acb08dccda1dcafeea00eef3a))
### Other
- Lint & format ([`12e4550`](https://github.com/Centers-health/dynpy/commit/12e45504acc9cd2c48695f7a598b0bae7770c1f4))

## v13.1.2 (2025-02-18)
### Fix
* Bugies ([`ec6e0b2`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ec6e0b28e7684d060c75351a62b8f17a60bef407))

## v13.1.1 (2025-02-17)
### Fix
* Optimize memory for virtual scroll ([`6514c33`](https://github.com/Centers-Health/dynamics-py-gfl/commit/6514c33c9e526e36b80a398d479d81c45a9ba556))

## v13.1.0 (2025-02-14)
### Feature
* Add virtual scrolling 🚀 ([`cf96810`](https://github.com/Centers-Health/dynamics-py-gfl/commit/cf96810ad7722a157b6f7d641a013326e8f23c92))

## v13.0.0 (2025-02-10)
### Fix
* Bump dynpy version to 19.0.0 ([`ff24083`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ff240839d777a8d18c2e5f356308f725173a90a9))
### Breaking
* bump dynpy version to 19.0.0 ([`ff24083`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ff240839d777a8d18c2e5f356308f725173a90a9))

## v12.1.6 (2025-02-10)
### Fix
* Fix bug in month selector when manually cleared ([`344f0e6`](https://github.com/Centers-Health/dynamics-py-gfl/commit/344f0e69d14a0435278965f928aded7f26177475))

## v12.1.5 (2025-02-05)
### Fix
* Update hx-requests to 0.35.2 and allow python any 3.x version ([`ece091d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ece091da1fbb85a28e829f2f634c9c3796728632))

## v12.1.4 (2025-02-04)
### Fix
* Update hx-requests to latest version ([`9fcdbce`](https://github.com/Centers-Health/dynamics-py-gfl/commit/9fcdbce3271470e4d515de6c5dc328eb08f615a3))

## v12.1.3 (2025-01-30)
### Fix
* Make split view table wrapper narrower to avoid scrollbar ([`6eac093`](https://github.com/Centers-Health/dynamics-py-gfl/commit/6eac093938e1189c950b78f5f3d964996cf1f27b))

## v12.1.2 (2025-01-26)
### Fix
* Force version bump ([`a2382be`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a2382be0f89d724b1c6435544d1cadf75d749df5))

## v12.1.1 (2025-01-17)
### Fix
* Remove use full path ([`fdef041`](https://github.com/Centers-Health/dynamics-py-gfl/commit/fdef0411f806b2a05dbde46593e03b6778ef9d77))

## v12.1.0 (2025-01-16)
### Feature
* Make side panel header sticky ([`8377a4b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/8377a4b233584c11069fe55f1f715e483137cbfe))

## v12.0.1 (2025-01-14)
### Fix
* Stop side panel from breaking when the obj doesn't exist in the default manager qs ([`cd3f1b0`](https://github.com/Centers-Health/dynamics-py-gfl/commit/cd3f1b012120776c3825327d01766b18071e701b))

## v12.0.0 (2025-01-14)
### Feature
* Change js-gfl-row to js-gfl-item ([`f8ec864`](https://github.com/Centers-Health/dynamics-py-gfl/commit/f8ec8642c16fe6e8e8cd63a2038cb18a988c0810))
* Move htmx_gfl_row_hidden_elems to include template ([`806ef36`](https://github.com/Centers-Health/dynamics-py-gfl/commit/806ef3640d994029cd6e6ee8ee40ccd680f389e6))
* Use .js-gfl-row to count total rows on htmx pages ([`b847063`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b847063be8af581b7f4572270dc4f7b1670c2a1a))
### Fix
* Convert more selectors to .js-gfl-row ([`e50e9d4`](https://github.com/Centers-Health/dynamics-py-gfl/commit/e50e9d46b93dd78515c759e5bbe12bf885b2a85a))
* Use js-gfl-row for hx-targets ([`ba2bbd5`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ba2bbd57b25337ad71b4aa55124319c9aa659666))
### Breaking
* Change js-gfl-row to js-gfl-item ([`f8ec864`](https://github.com/Centers-Health/dynamics-py-gfl/commit/f8ec8642c16fe6e8e8cd63a2038cb18a988c0810))
* Use .js-gfl-row to count total rows on htmx pages ([`b847063`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b847063be8af581b7f4572270dc4f7b1670c2a1a))

## v11.6.1 (2025-01-07)
### Fix
* Catch ValidationError if filter.to_python fails to stop page from crashing ([`7664b39`](https://github.com/Centers-Health/dynamics-py-gfl/commit/7664b39f4aebd728c66478364574ea355ca53280))

## v11.6.0 (2025-01-06)
### Feature
* Send rowId in table-row-removed event ([`1d2df5f`](https://github.com/Centers-Health/dynamics-py-gfl/commit/1d2df5f03043c62edce02b210ee51b7ee55860ba))
### Fix
* Check if row was replaced before firing table-row-removed event ([`7293499`](https://github.com/Centers-Health/dynamics-py-gfl/commit/7293499407c3ab6321b38e97b125f5a9f470c8d8))

## v11.5.2 (2025-01-01)
### Fix
* Fix frozen colmuns when using hx filters ([`3c2946a`](https://github.com/Centers-Health/dynamics-py-gfl/commit/3c2946ac3941b00617505ff7e5f04d12298fed06))

## v11.5.1 (2024-12-25)
### Fix
* Fix bug in tabs count ([`a9dd0a7`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a9dd0a7503ae62c984ffa1d6903860bbfe0f20c2))

## v11.5.0 (2024-12-25)
### Feature
* Update dynpy core version to 18.0.1 ([`364de8a`](https://github.com/Centers-Health/dynamics-py-gfl/commit/364de8a37fe2e600636f8fad9070daba5defa167))

## v11.4.0 (2024-12-25)
### Feature
* Update versions of dynpy core, forms, and actions ([`af97b0b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/af97b0bc724cd2a218224ce708a0a8c3dc3b06dd))

## v11.3.4 (2024-12-04)
### Fix
* Re-run freeze columns script on infinite scroll ([`c52740e`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c52740eb2cbee4120fe8a642330e23cf0d3104f9))

## v11.3.3 (2024-12-03)
### Fix
* Don't refresh tabs container when clicking tab ([`38230a4`](https://github.com/Centers-Health/dynamics-py-gfl/commit/38230a454779a52057817985e3143417804127ee))

## v11.3.2 (2024-12-03)
### Fix
* Add settle:0 to clicking on row to load side panel ([`2c53177`](https://github.com/Centers-Health/dynamics-py-gfl/commit/2c5317753baf897933d766e8fe3372212e7c3d5c))

## v11.3.1 (2024-12-02)
### Fix
* Add settle:0 to side panel hx request ([`a2a5d64`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a2a5d64aaffd8ac729f3680ac059ed552bfe69c1))

## v11.3.0 (2024-11-27)
### Feature
* Add tests ([`02ab419`](https://github.com/Centers-Health/dynamics-py-gfl/commit/02ab41997517d4d3a4a2e81146a44d623b31cc2a))
* Add custom filter method option ([`4918d08`](https://github.com/Centers-Health/dynamics-py-gfl/commit/4918d081345b4039aef28a272510fe1976c9dd82))
* Use cleaned value for filter value ([`eef4977`](https://github.com/Centers-Health/dynamics-py-gfl/commit/eef497770e8ddcbf8f9d3f1fc1012dc746ae5037))
* Add default empty option to filtered choice mixin ([`b564181`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b564181557cfa9d39dc0a5ec0c8a66b9e24f3bfc))
* Add distinct to filtered choice mixin ([`4f2bfd5`](https://github.com/Centers-Health/dynamics-py-gfl/commit/4f2bfd559713adfaa302c6e8b5bfd8412cc22798))

## v11.2.0 (2024-11-20)
### Feature
* Add hx-trigger to GFLExportAction when file is exported ([`231e2f6`](https://github.com/Centers-Health/dynamics-py-gfl/commit/231e2f6bec88765456f744e8630096094057884c))

## v11.1.0 (2024-11-19)
### Feature
* Copy over gfl action exporter from AR ([`a7bf6a1`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a7bf6a1e608197311537ebd7632a3f20779c79c3))

## v11.0.2 (2024-11-19)
### Fix
* Remove unnecessary check for paginated queryset ([`855df83`](https://github.com/Centers-Health/dynamics-py-gfl/commit/855df8353c0354196929f169d449ccfe64e8ec5b))

## v11.0.1 (2024-11-14)
### Fix
* Don't allow sorting by empty column ([`2ed819f`](https://github.com/Centers-Health/dynamics-py-gfl/commit/2ed819fb2fdc42a357076c2d307320c13df9118b))

## v11.0.0 (2024-11-14)
### Feature
* Prevent invalid default_order_fields ([`960b17a`](https://github.com/Centers-Health/dynamics-py-gfl/commit/960b17a265de05b7306e31ed5ee0aa34b22ff1b4))
* Cache results of qs in filtersets ([`7036478`](https://github.com/Centers-Health/dynamics-py-gfl/commit/703647824d7a953360f183c4fa51ca3b68ed28d2))
### Fix
* Account for sort direction in field check ([`773185f`](https://github.com/Centers-Health/dynamics-py-gfl/commit/773185fb3c4a254fdaa1d8827a60fd7b1980522b))
* Multiple queries when checking if can order by field ([`432a788`](https://github.com/Centers-Health/dynamics-py-gfl/commit/432a788f660e8cf8cdb821630a27b27bb7cc3dab))
### Breaking
* It raises an error if one of the fields in the default_order_fields is not a column on the page. This is to ensure that only columns on the page are added to the default_order_fields.  ([`960b17a`](https://github.com/Centers-Health/dynamics-py-gfl/commit/960b17a265de05b7306e31ed5ee0aa34b22ff1b4))
* This is breaking change because it changes the name of the "get_column_definitions" method in GenericFilterSet to"column_definitions". To handle this change, use "column_definitions" instead of "get_column_definitions".  ([`773185f`](https://github.com/Centers-Health/dynamics-py-gfl/commit/773185fb3c4a254fdaa1d8827a60fd7b1980522b))

## v10.0.5 (2024-11-07)
### Fix
* Apply selectpicker bug fix to extra filters (followup to c3d41be) ([`c0cd0ce`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c0cd0ce02d9686a0bf36a58f545f140f62115544))

## v10.0.4 (2024-10-14)
### Fix
* Make tabs more developer-friendly ([`63e7822`](https://github.com/Centers-Health/dynamics-py-gfl/commit/63e7822ef500a93ebd36781d1710aa52c556d962))
* Put the tab input in the filter form ([`659869b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/659869b9b280210e411e04dcca80486a32d521f6))

## v10.0.3 (2024-10-13)
### Fix
* Requested changes ([`135d2b5`](https://github.com/Centers-Health/dynamics-py-gfl/commit/135d2b5b419b74a9c128eb59d78ad01d86efa4d8))
* Requested changes ([`10c2c25`](https://github.com/Centers-Health/dynamics-py-gfl/commit/10c2c25e26c4703367cf909acdde5394e52a6c72))
* Fix htmx loader overlay ([`4f19f47`](https://github.com/Centers-Health/dynamics-py-gfl/commit/4f19f47426b5024e1c7828741d76762901edf602))

## v10.0.2 (2024-10-09)
### Fix
* Check order validity of order by overrides ([`7ea5d03`](https://github.com/Centers-Health/dynamics-py-gfl/commit/7ea5d03fe9a3c0ef9a59c548790fbf54c0b5bf1f))
* Column with invalid ordering should not display order arrow ([`8862b60`](https://github.com/Centers-Health/dynamics-py-gfl/commit/8862b605f68a8d04de16e196a3116a5414587942))

## v10.0.1 (2024-10-01)
### Fix
* Allow different ordering directions for default_order_fields ([`6d26dcc`](https://github.com/Centers-Health/dynamics-py-gfl/commit/6d26dcc711b5c811427d09fa8007f432e12971dc))

## v10.0.0 (2024-09-30)
### Fix
* Update dynpy core, actions, forms ([`830c085`](https://github.com/Centers-Health/dynamics-py-gfl/commit/830c085fa32892c5ed0731d1e574c04f5bb3b976))
### Breaking
* update dynpy core, actions, forms ([`830c085`](https://github.com/Centers-Health/dynamics-py-gfl/commit/830c085fa32892c5ed0731d1e574c04f5bb3b976))

## v9.3.1 (2024-09-24)
### Fix
* Fix missing span tag ([`e00330e`](https://github.com/Centers-Health/dynamics-py-gfl/commit/e00330eba110d0a922cf906ca19d501bb64b0dc2))
* Fix misnamed variable in split_view_htmx.html ([`7ff113a`](https://github.com/Centers-Health/dynamics-py-gfl/commit/7ff113a0630cbf8cde8fdc77203d919ba71c1da3))

## v9.3.0 (2024-09-24)
### Feature
* Add opt-in index column to Htmx GFL tables ([`5393b1c`](https://github.com/Centers-Health/dynamics-py-gfl/commit/5393b1c930f2c36eb0de7a5008e30a76d4aa8012))

## v9.2.2 (2024-09-11)
### Fix
* Split view htmx duplicating the same rows on infinite scroll ([`30eee92`](https://github.com/Centers-Health/dynamics-py-gfl/commit/30eee92af63981ba78616cf5fddfc15a5632926b))

## v9.2.1 (2024-09-10)
### Fix
* Add back dynamic hx-trigger attribute based on alpine state ([`372d044`](https://github.com/Centers-Health/dynamics-py-gfl/commit/372d0441f6083eb42b4a1a7d6c9ffd30fc56022e))

## v9.2.0 (2024-09-10)
### Feature
* Add refresh side panel trigger functionality ([`2bc86f0`](https://github.com/Centers-Health/dynamics-py-gfl/commit/2bc86f0a430e86b852b039da5d394e6c66ab78a8))
### Fix
* Prevent child elements from inheriting hx-indicator ([`72c4a41`](https://github.com/Centers-Health/dynamics-py-gfl/commit/72c4a41ec2f771f13135d6da962c5fff1780ad86))

## v9.1.1 (2024-09-09)
### Fix
* Clicking in side panel refeshing ([`b387140`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b387140c8382046a1c091cb1f5ed553d6438a779))

## v9.1.0 (2024-09-04)
### Feature
* Update hx-requests to 0.32.1 (latest) ([`ad29ed1`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ad29ed15184599c8e0bb21175088ff28e89143ef))

## v9.0.1 (2024-09-04)
### Fix
* Fix bug in infinite scroll ([`d413414`](https://github.com/Centers-Health/dynamics-py-gfl/commit/d413414376afced2641a16a00337df8c9abf8767))

## v9.0.0 (2024-09-03)
### Feature
* Upgrade Django to v4.2.x ([`673321b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/673321b0575e067f1a78bd2565dc47bc689e3903))
### Breaking
* Upgrade Django to v4.2.x ([`673321b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/673321b0575e067f1a78bd2565dc47bc689e3903))

## v8.3.0 (2024-09-02)
### Feature
* Add placeholder blocks to gfl template ([`d92cb97`](https://github.com/Centers-Health/dynamics-py-gfl/commit/d92cb97ffd5e0d846bfbe9d20b02137cd45c84ac))

## v8.2.1 (2024-08-29)
### Fix
* Hide resizer when side panel is closed ([`e82cf10`](https://github.com/Centers-Health/dynamics-py-gfl/commit/e82cf10ef1dcdc191c9a772764d665f1989c52ad))
* Add delay for intersect trigger on the htmx split view ([`148ec10`](https://github.com/Centers-Health/dynamics-py-gfl/commit/148ec108beaaa1b299a7e9f7b3c68890f7fd53b4))
* Infinite scroll not triggering when element is out of ([`ec1d3da`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ec1d3daea7e90865d8c4953cca58f848ad27d7d6))

## v8.2.0 (2024-08-28)
### Feature
* Add Esc key shortcut to close side panel ([`ce7884e`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ce7884e57fbc46a60684b79ed0ade1fe6a0d32f5))

## v8.1.0 (2024-08-27)
### Feature
* Prevent user selection when resizing ([`69b6f44`](https://github.com/Centers-Health/dynamics-py-gfl/commit/69b6f441229c58b5597a8f096c05cf952dc31a64))
* Change cursor on entire window when resizing ([`a83deba`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a83deba4a44afb6da68e495c3bffde116d76703a))
* Update resize element styles and add hover effect ([`1711b6d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/1711b6dbb8df7c3fc0db4dce4412e5d2cbaddc29))
### Fix
* Add paginator table row counter to split view ([`bed289f`](https://github.com/Centers-Health/dynamics-py-gfl/commit/bed289fd9bc2e0e5d272263b1db59ef65c6e7007))
* Fix extra space to the right of close button ([`2f95907`](https://github.com/Centers-Health/dynamics-py-gfl/commit/2f95907562882c105a5127a1e3fa771031acc42d))
* Infinite scroll not triggering when element is out of view ([`36c203c`](https://github.com/Centers-Health/dynamics-py-gfl/commit/36c203c1b9825b49a86fa73e13ff93dc57c86a14))
* Fix resize side panel ([`7346864`](https://github.com/Centers-Health/dynamics-py-gfl/commit/73468641ea62e6197a7f4e017f4e755dae3df908))

## v8.0.0 (2024-08-22)
### Feature
* Update the paginator position to be based off <tr> count ([`904714a`](https://github.com/Centers-Health/dynamics-py-gfl/commit/904714ac543ccba23a3e59d8b73d450658b948dd))
### Fix
* Update RefreshRow to use outerHTML swap ([`40355e7`](https://github.com/Centers-Health/dynamics-py-gfl/commit/40355e72da94ae526a9c7745cdc23d144b49d8ca))
### Breaking
* This change will break the functionality of the RefreshRow HX request. It will now replace the entire row instead of just the content of the row. The GET_block has been updated to "table_row_outer" to reflect this change (if inheriting from the RefreshRow class you may need to update GET_block because the default has changed).  ([`40355e7`](https://github.com/Centers-Health/dynamics-py-gfl/commit/40355e72da94ae526a9c7745cdc23d144b49d8ca))

## v7.6.0 (2024-08-16)
### Feature
* Set default pagination to 20 in GFLSplitViewHX ([`c4aac36`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c4aac36c5e228c26b82c02e8a3ffaa884f4257a8))

## v7.5.0 (2024-08-14)
### Feature
* Fetch count on Gfls async via htmx ([`662ed30`](https://github.com/Centers-Health/dynamics-py-gfl/commit/662ed30af94550532a0210fa69964619e1b46742))
* Add InfiniteScrollPaginator to dynpy_gfl ([`403e750`](https://github.com/Centers-Health/dynamics-py-gfl/commit/403e7506fced23f45a5ce12cc27c6f87f1654e15))
### Fix
* Format GFL total count with commas ([`06e2ee0`](https://github.com/Centers-Health/dynamics-py-gfl/commit/06e2ee0ac758714e7a57cbe4d8a865b5727d9e9f))
* Change loader for gfl total count ([`0189a3f`](https://github.com/Centers-Health/dynamics-py-gfl/commit/0189a3f0eb6b3b8fe5bfa1d1a5038a402589016b))
* Clean up paginator ([`6f82b1b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/6f82b1bc6756e0f930d0f23cb0d34d745169d5cf))

## v7.4.1 (2024-08-07)
### Fix
* Fix bug in get_queryset on GenericFilterListViewHX ([`2470a80`](https://github.com/Centers-Health/dynamics-py-gfl/commit/2470a80227f345932a36725e4d7370a37541f869))

## v7.4.0 (2024-08-07)
### Feature
* Add a way to handle tabs on the htmx gfl ([`8864792`](https://github.com/Centers-Health/dynamics-py-gfl/commit/8864792a77a35cb13bfb1b904c816b74b7d529f6))
### Fix
* Add processing for tabs to dynpy_gfl ([`ae7d8cb`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ae7d8cbbe3b6ff716a53f266b2c7cf5eda3b3373))

## v7.3.1 (2024-07-23)
### Fix
* Remove fast paginator ([`747c533`](https://github.com/Centers-Health/dynamics-py-gfl/commit/747c533f3bad7cbe66341c4e95ea50b2e8a17414))

## v7.3.0 (2024-07-19)
### Feature
* Add the custom_views_get to the gfl views ([`e234d42`](https://github.com/Centers-Health/dynamics-py-gfl/commit/e234d421cdbb46860ae641e67b1eefb952d5b00d))
* Modify the hx view to invalidate the cache when not scrolling ([`9b48b06`](https://github.com/Centers-Health/dynamics-py-gfl/commit/9b48b06af7f76941bd8a157ac8d4ef71c5d5241e))
* Refactor infinite scroll to start earlier ([`47c5408`](https://github.com/Centers-Health/dynamics-py-gfl/commit/47c54085b46f18ed88e07e124b2e60a4224325ed))
### Fix
* Remove not needed InfiniteScrollSplitView class ([`dfb1b3d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/dfb1b3d9260da46ae0df5f1c4ecda3b3a3588a69))

## v7.2.1 (2024-07-19)
### Fix
* Remove fast paginator as the default ([`b2fa818`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b2fa818140b5f78b6a0c995089c06d070959291e))

## v7.2.0 (2024-07-18)
### Feature
* Add a fast paginator for Django ([`f5f9f16`](https://github.com/Centers-Health/dynamics-py-gfl/commit/f5f9f16d59cf8de438af4aa9d67ed9a55b5f56f6))

## v7.1.2 (2024-07-17)
### Fix
* Fix weird css bug with bordered tables ([`6d198a8`](https://github.com/Centers-Health/dynamics-py-gfl/commit/6d198a8f8bdc64cbf15209722ce66c177b8f5558))

## v7.1.1 (2024-07-17)
### Fix
* Move pytest-random-order to dev dependencies ([`8ce73ab`](https://github.com/Centers-Health/dynamics-py-gfl/commit/8ce73ab9115dba126d246463ebc6cd01c5adc102))

## v7.1.0 (2024-07-16)
### Feature
* Add defaults to RefreshRow so that it does not need overriding ([`a618264`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a618264e8ff8a6491aa6cfee167d7ade3312f8b1))
* Add block for refresh_row_indicator ([`3ba1343`](https://github.com/Centers-Health/dynamics-py-gfl/commit/3ba13430131f00a804bed707766446f52d57c77f))
* Add css for hidden-invisible class ([`ebc135d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ebc135d799fa72430750b26567994b0ea575d6e3))
* Add refresh row to GFL ([`21a6ce3`](https://github.com/Centers-Health/dynamics-py-gfl/commit/21a6ce3b19911ea5230ead7e5e563a2318150455))
* Add block for above the table ([`253671d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/253671d2e61fb2b1ba695500df461a6b98f461e4))
### Fix
* Move invisible tds to the table row block ([`69db30d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/69db30d906317a9651d28eccf998c8d3172ac047))
* Fix scroll issue when using a bootstrap bordered table ([`f2d2023`](https://github.com/Centers-Health/dynamics-py-gfl/commit/f2d20236dde1cfefbdebe918c02e732fdb0a319c))
* Refresh totals and no objects message when filter ([`de32bfb`](https://github.com/Centers-Health/dynamics-py-gfl/commit/de32bfbf2792eaab8d749f79cae3bdafd2f8af90))

## v7.0.1 (2024-07-08)
### Fix
* Make split view table narrower to make room for resizer ([`26f2ec0`](https://github.com/Centers-Health/dynamics-py-gfl/commit/26f2ec035bbfcebd764b75a1d7cb2851f7b5d473))

## v7.0.0 (2024-07-01)
### Feature
* Add side panel load trigger ([`741506d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/741506ddc42b93a8f727f7b2a6d5db2155f8dff0))
* Move table loader to not overlay the side panel ([`30df0b5`](https://github.com/Centers-Health/dynamics-py-gfl/commit/30df0b545ccd31f87fe8fbdb921b6acf91cf8009))
* Enhance side panel transition ([`dd58db4`](https://github.com/Centers-Health/dynamics-py-gfl/commit/dd58db4e4a46f2b598b5063220aa2524798b52d8))
* Add object_id to url to make shareable ([`3029f4d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/3029f4d4df2414f55857abdb736eee34aa7f9e2e))
* Load active row side panel data on page load ([`72024c8`](https://github.com/Centers-Health/dynamics-py-gfl/commit/72024c84fe70d2625e003a39d467952fe8656562))
* Keep side panel data when filtering or sorting ([`89c63a0`](https://github.com/Centers-Health/dynamics-py-gfl/commit/89c63a0dfa34bf621aea2e3fac0323ee1ecc8179))
### Breaking
* keep side panel data when filtering or sorting ([`89c63a0`](https://github.com/Centers-Health/dynamics-py-gfl/commit/89c63a0dfa34bf621aea2e3fac0323ee1ecc8179))
### Documentation
* Add comment for django-render-block inheritance issue ([`8d0b62f`](https://github.com/Centers-Health/dynamics-py-gfl/commit/8d0b62fd8c9f7ed2531231c24668a046f693ae3f))

## v6.0.2 (2024-06-24)
### Fix
* Filtering not maintaining sort order ([`09d85dc`](https://github.com/Centers-Health/dynamics-py-gfl/commit/09d85dc588c4ae6a87943db0353b3892b54a1f8b))

## v6.0.1 (2024-06-20)
### Fix
* Fix bug when binding htmx attr via Alpine.js ([`0f65cf3`](https://github.com/Centers-Health/dynamics-py-gfl/commit/0f65cf3f2886fdbffd56609fde49a06d51bbc436))
* Fix bugs with alpine state ([`841143d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/841143d573ed9cc6f3a4a2d8679a8aeedcfbdf29))

## v6.0.0 (2024-06-05)
### Feature
* Make split view using htmx / alpine ([`98a7156`](https://github.com/Centers-Health/dynamics-py-gfl/commit/98a7156e70df5c8a06d9f6fea160a553f263f021))
### Breaking
* make split view using htmx / alpine ([`98a7156`](https://github.com/Centers-Health/dynamics-py-gfl/commit/98a7156e70df5c8a06d9f6fea160a553f263f021))

## v5.4.0 (2024-05-23)
### Feature
* Use bs to animate htmx gfl filter & extra filter collapse ([`b9f01ca`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b9f01ca217a8c041633a43b4dfa9af6181608c2c))
### Fix
* Prevent htmx table from disappearing when filtering/sorting ([`e7a682d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/e7a682dabc1fd114aec06a75f3f1c81440aab09e))
* Make htmx gfl template only scroll on the table body ([`01a4c22`](https://github.com/Centers-Health/dynamics-py-gfl/commit/01a4c228c5407d12ec0c35d1059048a424358655))

## v5.3.1 (2024-05-21)
### Fix
* Update dynpy core to 15.0.0 ([`e84954e`](https://github.com/Centers-Health/dynamics-py-gfl/commit/e84954e8c488d6ad85ea7b31f3939e6001f9e5ed))

## v5.3.0 (2024-05-14)
### Feature
* Allow for dynamic frozen column count ([`0424592`](https://github.com/Centers-Health/dynamics-py-gfl/commit/042459279199b1f993455e8eff6f6b6873a28c46))

## v5.2.1 (2024-05-01)
### Fix
* Remove required column parameter from column_header_link ([`cd183e5`](https://github.com/Centers-Health/dynamics-py-gfl/commit/cd183e50835bca0dc0fff870908f95f18cb30e05))

## v5.2.0 (2024-04-16)
### Feature
* Add ability to override ordering with Expression ([`b3b4bed`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b3b4bededb6fa49cfa0096c38a13b43a70bbcc8e))
### Fix
* Change error message for ordering ([`ec37be8`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ec37be829908e6c1c5992a19508a766eaaa49cea))
* Clean up column_header_link tag and extend to work with new overrides ([`ebfcb81`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ebfcb81f1597bb8e3cb987d64e677f08e26e8aef))

## v5.1.0 (2024-03-27)
### Feature
* Add ability to override no objects text gfl htmx template ([`9830d75`](https://github.com/Centers-Health/dynamics-py-gfl/commit/9830d75ca40120c732e1c91ceccf208eb1694c64))
* Add trigger for filtered ([`fdfe85b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/fdfe85b2d76125ae02238f4375171d8951633ef3))

## v5.0.1 (2024-03-13)
### Fix
* Fix bug in infinite scroll ([`aa71b9b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/aa71b9bd605e9bc05a33a6183e1a87f14c1a9bb6))

## v5.0.0 (2024-03-06)
### Fix
* Update gfl row ID for HTML compliance ([`30df4d4`](https://github.com/Centers-Health/dynamics-py-gfl/commit/30df4d41e10d091b2f90bac5e4b277951687c977))
### Breaking
* update gfl row ID for HTML compliance ([`30df4d4`](https://github.com/Centers-Health/dynamics-py-gfl/commit/30df4d41e10d091b2f90bac5e4b277951687c977))

## v4.8.1 (2024-02-16)
### Fix
* Incorrect paginate by option selected ([`334b376`](https://github.com/Centers-Health/dynamics-py-gfl/commit/334b376552542e88126bd91f9bd9a37c0e2f7182))

## v4.8.0 (2024-02-15)
### Feature
* Add table_row_attributes to each table row ([`f9ef1e1`](https://github.com/Centers-Health/dynamics-py-gfl/commit/f9ef1e1eba13cde69a5690482db6458745fc83a3))

## v4.7.1 (2024-02-14)
### Fix
* Change the way selectpickers are handled in the filter form ([`c3d41be`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c3d41be1f260392de1f3a4912e8fe1aaee9c3216))

## v4.7.0 (2024-02-13)
### Feature
* Add ability to add custom pagination options ([`e41f9fb`](https://github.com/Centers-Health/dynamics-py-gfl/commit/e41f9fbbd1f5f7e4ccb7e5d56bb2f9e7c008abee))

## v4.6.2 (2024-02-08)
### Fix
* Allow for latest version of hx-requests ([`1a205e6`](https://github.com/Centers-Health/dynamics-py-gfl/commit/1a205e630957ebbdc2c3ef785720b761f449ebae))

## v4.6.1 (2024-01-25)
### Fix
* Scope selectpicker change to the one in the filter form ([`f9e5227`](https://github.com/Centers-Health/dynamics-py-gfl/commit/f9e5227cb3ce0186e96f70a08ec05fae75c832e4))

## v4.6.0 (2024-01-23)
### Feature
* Add htmx and alpine.js support to generic filter list view ([`0a53d69`](https://github.com/Centers-Health/dynamics-py-gfl/commit/0a53d699fca4618f81f6f82b152566011b40ecf6))
* Add htmx sorting to the gfl table ([`8645792`](https://github.com/Centers-Health/dynamics-py-gfl/commit/864579252ffcd07ab40486fcc3d5a33ea27822ad))
### Fix
* Refactor trigger for htmx filter ([`5454abb`](https://github.com/Centers-Health/dynamics-py-gfl/commit/5454abb2e1b39f0f49e60ac951ab070f3ea866dc))
* Remove alpine_styles ([`dab223a`](https://github.com/Centers-Health/dynamics-py-gfl/commit/dab223a65b28dc91cd571ad85c8fb0edfcffd945))
* Remove htmx_styles.css from htmx template ([`50cc653`](https://github.com/Centers-Health/dynamics-py-gfl/commit/50cc653f3ac6b5defd0556b13e317a75ede79c59))
* Remove CDNs from generic_filter_list_htmx.html ([`4fa3a58`](https://github.com/Centers-Health/dynamics-py-gfl/commit/4fa3a587a35214922666f8f618903aecc2094b7b))
* Fix issue with selectpicker on change triggering too early ([`5400ce4`](https://github.com/Centers-Health/dynamics-py-gfl/commit/5400ce4eac817568bc66a4c102cf52a5b691434c))
* Change hx-select and select-oob to target and swap all gfl_content ([`692bbfe`](https://github.com/Centers-Health/dynamics-py-gfl/commit/692bbfe0e64aec12059355c6342863e96f4fddf0))
* Align the total to the right ([`de931db`](https://github.com/Centers-Health/dynamics-py-gfl/commit/de931db12931adcc3959df1c9dacb5d2bc5ac051))
* Update hx-requests to 0.18.0 ([`5cc941e`](https://github.com/Centers-Health/dynamics-py-gfl/commit/5cc941ede7267605c3e6b599e68f84183bd27f9b))
* Add alpine JS x-cloak for better page load experience ([`d092cdc`](https://github.com/Centers-Health/dynamics-py-gfl/commit/d092cdca2864775ba4dc79cfced765eb18ad0688))
* Add htmx styles ([`9ec3a2b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/9ec3a2b836ad7c015f30f2d219523b08caabd4a8))

## v4.5.1 (2024-01-18)
### Fix
* Update row-active class to improve visibility ([`879321f`](https://github.com/Centers-Health/dynamics-py-gfl/commit/879321f9b12681e8e133c2e7d96b1b0b308a9b4c))

## v4.5.0 (2024-01-11)
### Feature
* Add way to opt out of using side panel cache ([`b27c173`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b27c173bc6db6b31e729a8af7722bf37ccbeac8f))

## v4.4.0 (2024-01-09)
### Feature
* Add ability to hide filters ([`32802fa`](https://github.com/Centers-Health/dynamics-py-gfl/commit/32802fa51b07c2ab62ad549dc3d909aba8742eb2))

## v4.3.7 (2024-01-09)
### Fix
* Fix bug causing collapsed filters not to persist ([`f7473e7`](https://github.com/Centers-Health/dynamics-py-gfl/commit/f7473e73ac9ee0d076b8084fa3519e959daaf047))

## v4.3.6 (2024-01-09)
### Fix
* Highlighting rows but no side panel ([`bf5e50a`](https://github.com/Centers-Health/dynamics-py-gfl/commit/bf5e50a574b554e323d1706f205b03b470bab544))

## v4.3.5 (2024-01-09)
### Fix
* Highlight even on side panel opt out ([`ed065ad`](https://github.com/Centers-Health/dynamics-py-gfl/commit/ed065ad6ee0c3d1300f43468ac23fb6876185e91))

## v4.3.4 (2024-01-04)
### Fix
* Gfl table not filling up page when 1 row ([`3257da0`](https://github.com/Centers-Health/dynamics-py-gfl/commit/3257da05e153531dfb7ce465d12de3a219d4c54a))

## v4.3.3 (2024-01-04)
### Fix
* Revert "feat: update application of default filters to account for saved filters" ([`3576d0f`](https://github.com/Centers-Health/dynamics-py-gfl/commit/3576d0fed72eae5d83fc962d8a64f3c07e77334a))

## v4.3.2 (2024-01-03)
### Fix
* Update actions to 4.0.0 ([`a394bf6`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a394bf63c3cf5a1fe856fafc06bc1b323f7e14c5))

## v4.3.1 (2024-01-03)
### Fix
* Remove dynpy-cas dependency ([`b78177e`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b78177e10fd7adfd0cd3f137a93d652dd9818cc5))

## v4.3.0 (2023-12-29)
### Feature
* Update application of default filters to account for saved filters ([`a9b3420`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a9b3420b17e34f5b2bad419c9758d99bce252427))

## v4.2.0 (2023-12-27)
### Feature
* Use border for active row instead of background color ([`3e8af29`](https://github.com/Centers-Health/dynamics-py-gfl/commit/3e8af29e49a94d9aa1af9b8e5bfc794a75e0d47c))

## v4.1.0 (2023-12-27)
### Feature
* Keep side panel closed for aging notes ([`02922f3`](https://github.com/Centers-Health/dynamics-py-gfl/commit/02922f30a07f2ddf55b815f90589afe4e57980ad))

## v4.0.2 (2023-12-25)
### Fix
* Can resize when side panel is closed ([`0f2fee2`](https://github.com/Centers-Health/dynamics-py-gfl/commit/0f2fee22d1d063f10d9a11d08bf09accec1fc2a7))
* Make resizing panel work on all gfl pages ([`c52d8c7`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c52d8c713545b78e6a97fb9a514e053d11ba2cf1))

## v4.0.1 (2023-12-14)
### Fix
* Upgrade dynpy js dependencies ([`d693a64`](https://github.com/Centers-Health/dynamics-py-gfl/commit/d693a64718cc2bcc14e4a6d0f763b59fa630905b))

## v4.0.0 (2023-12-13)
### Feature
* Upgrade python 3.8 ~> 3.11 ([`c9f9988`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c9f998884c962f31a2a21b44d0c2b3ec982aabf4))
### Fix
* Upgrade dynpy dependencies ([`592f090`](https://github.com/Centers-Health/dynamics-py-gfl/commit/592f090399d54872fbafc16dea50a632b3fc9493))
### Breaking
* upgrade python 3.8 ~> 3.11 ([`c9f9988`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c9f998884c962f31a2a21b44d0c2b3ec982aabf4))

## v3.5.0 (2023-12-13)
### Feature
* Update dynpy version (13.0.0) ([`a3d5b87`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a3d5b872702e5cee88729d7bb11fe46658147cbc))

## v3.4.0 (2023-12-12)
### Feature
* Upgrade dynpy compatibility (>=8.0.0,<11.0.0) ([`679f286`](https://github.com/Centers-Health/dynamics-py-gfl/commit/679f286c2dc6757466d02c2abd578b328f4f9c34))

## v3.3.0 (2023-11-29)
### Feature
* Upgrade dynpy compatibility (>=8.0.0,<10.0.0) ([`b29dcdf`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b29dcdf6b8754194ccbbef790a0256ddd82c654b))

## v3.2.0 (2023-10-18)
### Feature
* Update dynpy to 8.0.0 ([`af99ff8`](https://github.com/Centers-Health/dynamics-py-gfl/commit/af99ff885ef86a4c2c3a9138b8a92b25c67d739b))

## v3.1.0 (2023-09-21)
### Feature
* Allow clickable elements in split view that don't open side panel ([`5638114`](https://github.com/Centers-Health/dynamics-py-gfl/commit/5638114a6aa0ced8bbed052e32d21e606e21dc3b))

## v3.0.0 (2023-09-14)
### Feature
* Return TemplateResponse for side panel ([`fdaea1d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/fdaea1d58400ddb78a20c1e8c8355badb0c439f8))
### Breaking
* return TemplateResponse for side panel ([`fdaea1d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/fdaea1d58400ddb78a20c1e8c8355badb0c439f8))

## v2.23.0 (2023-09-14)
### Feature
* Update dynpy_actions ([`36dce30`](https://github.com/Centers-Health/dynamics-py-gfl/commit/36dce300b0d0a01423316104fcded29a56657f79))

## v2.22.0 (2023-09-13)
### Feature
* Upgrade dnypy to 7.1.0 ([`438e6f4`](https://github.com/Centers-Health/dynamics-py-gfl/commit/438e6f49ba7d7ea26567a9209edafc17c3cb5626))

## v2.21.0 (2023-09-06)
### Feature
* Upgrade dynpy compatibility (>=4.2.0,<7.0.0) ([`5a4ff5a`](https://github.com/Centers-Health/dynamics-py-gfl/commit/5a4ff5a738f4df8cace58041a709b76aec38d6dd))

## v2.20.1 (2023-08-31)
### Fix
* Add option to split view to ignore cache ([`1b97dae`](https://github.com/Centers-Health/dynamics-py-gfl/commit/1b97dae56da82e48d2cf8f18ba95282bcad3572e))
* Bug fix for when returning JsonResponse from action ([`53e6838`](https://github.com/Centers-Health/dynamics-py-gfl/commit/53e6838e487a32ae87135944b5313cf97be62c59))

## v2.20.0 (2023-08-31)
### Feature
* Move per page filter to end of row ([`8d0ec54`](https://github.com/Centers-Health/dynamics-py-gfl/commit/8d0ec54f505f9d39fd4e06f5bc9f813a720821e5))

## v2.19.2 (2023-08-10)
### Fix
* Fix bug in highlighting row class ([`6895247`](https://github.com/Centers-Health/dynamics-py-gfl/commit/6895247bd033ae6436cf37e2702c88386b6735b5))

## v2.19.1 (2023-07-19)
### Fix
* Don't allow resizing of side panel if closed ([`acf7349`](https://github.com/Centers-Health/dynamics-py-gfl/commit/acf7349b1394416fbe8672739d14f00cceaa906b))

## v2.19.0 (2023-07-18)
### Feature
* Put collapse filter button first ([`6505411`](https://github.com/Centers-Health/dynamics-py-gfl/commit/6505411f3ec4685f0eeee354186af5f57fb1c7ee))

## v2.18.0 (2023-07-11)
### Feature
* Add filer settings block ([`b8cb13d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b8cb13d10fefcf852c6907b42374aed8ea4c8055))
### Fix
* Use correct collapse/expand icon ([`f8b93ca`](https://github.com/Centers-Health/dynamics-py-gfl/commit/f8b93cae20fd2525eb6ac7d4870d86fca8723c4f))

## v2.17.3 (2023-07-06)
### Fix
* Fix regex not matching correctly ([`f73ad77`](https://github.com/Centers-Health/dynamics-py-gfl/commit/f73ad7751ee8439b217c7c00f7a7b8f7923afa14))

## v2.17.2 (2023-07-06)
### Fix
* Fix is_filtered to account for range filters ([`34a1552`](https://github.com/Centers-Health/dynamics-py-gfl/commit/34a1552d0c4bf54738bdcbe6be66df92b4f624bc))

## v2.17.1 (2023-07-03)
### Fix
* Refactor is_filtered to check data and not request ([`3e953d1`](https://github.com/Centers-Health/dynamics-py-gfl/commit/3e953d1d2cfd33d361da88de7a0d35bbf3a6888b))

## v2.17.0 (2023-06-30)
### Feature
* Add default_filters to GenericFilterListView ([`a98462b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a98462ba76573c1eb33e6621373db15bc310fbe8))

## v2.16.0 (2023-06-21)
### Feature
* Speed up resizing of side panel ([`2083ee3`](https://github.com/Centers-Health/dynamics-py-gfl/commit/2083ee3ed9453bb543b3bd3c28d34c830e0bb3ef))

## v2.15.0 (2023-06-15)
### Feature
* Make side panel resizeable ([`c5e7507`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c5e75071557a9e22162d14a712e7b3131f0147f2))

## v2.14.0 (2023-06-07)
### Feature
* Update dynpy actions version ([`2d22bb4`](https://github.com/Centers-Health/dynamics-py-gfl/commit/2d22bb4201edd0ac0a670c9e4a0b62baebd97eeb))

## v2.13.3 (2023-05-09)
### Fix
* Fix js bug 'offsetTop' ([`c6f65c0`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c6f65c0fc45c0b730d547efbb87ad51008ecb0c2))

## v2.13.2 (2023-04-24)
### Fix
* Remove label_from_instance from FilteredChoicesMixin ([`46c478a`](https://github.com/Centers-Health/dynamics-py-gfl/commit/46c478a67f2075d05691240fb5137450975d897d))

## v2.13.1 (2023-04-21)
### Fix
* Cast data to MultiValueDict in case it comes in as a dict ([`a96d393`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a96d3937a963f4c81f0678d5b4e94adb73e664a4))

## v2.13.0 (2023-04-19)
### Feature
* Add FilteredChoicesMixin ([`09336b4`](https://github.com/Centers-Health/dynamics-py-gfl/commit/09336b491117f4e6ea4ed4b8df43ea673809c65d))
### Fix
* Add flakeheaven_cache to gitignore ([`d9c446a`](https://github.com/Centers-Health/dynamics-py-gfl/commit/d9c446a2dbc86178dbfaa1f65ed2c9d37d277179))

## v2.12.1 (2023-04-04)
### Fix
* Updating dynpy_forms version ([`62ac794`](https://github.com/Centers-Health/dynamics-py-gfl/commit/62ac794d27690caf3d11e0ae9e055243227c9e7f))

## v2.12.0 (2023-03-27)
### Feature
* Add dynpy 5 compatibility ([`7739f64`](https://github.com/Centers-Health/dynamics-py-gfl/commit/7739f64ff33dfa44cc2d2c0e112f71262ddeba03))

## v2.11.0 (2023-03-23)
### Feature
* Update dynpy-forms version (>=2.0.0,<3.0.0) ([`52c38f9`](https://github.com/Centers-Health/dynamics-py-gfl/commit/52c38f98f6fe9447abb2a206435af223746d8e7f))

## v2.10.2 (2023-03-22)
### Fix
* Prevent double deploy from occurring ([`5d3bc2b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/5d3bc2bd4b169e1b458b3a6d2f9bc4be58743029))

## v2.10.1 (2023-03-16)
### Fix
* Update dynpy forms ([`cf1e53d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/cf1e53d58f94d5e3b2386091507f7bfcb15d634b))

## v2.10.0 (2023-03-13)
### Feature
* Refactor to use templatetags from dynpy ([`3425f9e`](https://github.com/Centers-Health/dynamics-py-gfl/commit/3425f9e9b29ea761096c78a65b6eb4b068a1e87e))

## v2.9.0 (2023-03-13)
### Feature
* Artificia change to bump version ([`b9dd0d7`](https://github.com/Centers-Health/dynamics-py-gfl/commit/b9dd0d74b72cc1f3bcebe3eab3e76ef4d4d2e016))

## v2.8.1 (2023-03-10)
### Fix
* Run pre-push hooks on ci ([`82788ac`](https://github.com/Centers-Health/dynamics-py-gfl/commit/82788ac6a414554863cccaba6953f754bedaf471))

## v2.8.0 (2023-03-06)
### Feature
* Add dynpy version compatibility (^4.0.0) ([`e895b23`](https://github.com/Centers-Health/dynamics-py-gfl/commit/e895b23f38dc2d19c5134c20a368c870bad0fca0))

## v2.7.0 (2023-03-02)
### Feature
* Add filters from AR; install dynpy@^3.7.0 ([`0f6f166`](https://github.com/Centers-Health/dynamics-py-gfl/commit/0f6f16687c33e0ae69d37585dcbce388869207ed))

## v2.6.1 (2023-02-20)
### Fix
* Add bubbling to the sidePanelLoad event ([`3a15507`](https://github.com/Centers-Health/dynamics-py-gfl/commit/3a155074ad2a6d18864710915a470a46e18c37e2))

## v2.6.0 (2023-02-16)
### Feature
* Add actions block ([`c5b36eb`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c5b36eb805e319b25d89588b32d10155a12fb327))

## v2.5.0 (2023-01-30)
### Feature
* Replace enable_custom_filter_view with use_filtered_qs_in_field ([`c96322d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c96322d0b9e0fc71e03ef754c728b5bb67396ebc))

## v2.4.3 (2023-01-27)
### Fix
* Fix issue with frozen columns ([`7c15626`](https://github.com/Centers-Health/dynamics-py-gfl/commit/7c156266e9e82c66cb88bd63d25ae801743f6fe4))

## v2.4.2 (2023-01-27)
### Fix
* Stop param_replace from removing empty filters ([`1f0c96f`](https://github.com/Centers-Health/dynamics-py-gfl/commit/1f0c96fd12861c5a0b52dfaf518b841e7fca4440))

## v2.4.1 (2023-01-24)
### Fix
* Delete cached fields when regenerating filter form ([`8c2d4d2`](https://github.com/Centers-Health/dynamics-py-gfl/commit/8c2d4d282e428bb4b4a8e2f267df89c16d8316a7))

## v2.4.0 (2023-01-23)
### Feature
* Add opt-in for CustomFilterView ([`0cdd9fc`](https://github.com/Centers-Health/dynamics-py-gfl/commit/0cdd9fc47ee957d1c41c1a5a60b2c2b2a988f597))

## v2.3.1 (2023-01-23)
### Fix
* Improve performace in CustomFilterView ([`dc07a86`](https://github.com/Centers-Health/dynamics-py-gfl/commit/dc07a86f039bfddce14e39f76faece13dd1a1311))

## v2.3.0 (2023-01-20)
### Feature
* Replace table-primary with custom class for active split view row ([`dee18de`](https://github.com/Centers-Health/dynamics-py-gfl/commit/dee18dec02f728d28228d4781f1e7c7a4f07d315))
* Add tbody block to generic_filter_list.html ([`c133748`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c133748e6302a079626fd1a45ef230052a9e1352))

## v2.2.0 (2023-01-19)
### Feature
* Reset filter form fields to give access to filtered qs ([`584d769`](https://github.com/Centers-Health/dynamics-py-gfl/commit/584d769275a50829c97edd04e383f7a900b01eae))

## v2.1.0 (2023-01-09)
### Feature
* Force version update ([`22e11b0`](https://github.com/Centers-Health/dynamics-py-gfl/commit/22e11b0f3ef6d4a53ad8abf5dc653390db1a23bb))
### Documentation
* Add dynpy_js to INSTALLED_APPS ([`a8189fa`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a8189fa66835154deddb50a6aa6d960d36dcef9d))
* Add humanize to the list of INSTALLED_APPS ([`1888594`](https://github.com/Centers-Health/dynamics-py-gfl/commit/1888594aa629cb2727e5e00aaf4c45fe25fb9349))

## v2.0.1 (2022-12-19)
### Fix
* Check if gfl table exists before creating ResizeObserver ([`abf84e1`](https://github.com/Centers-Health/dynamics-py-gfl/commit/abf84e117ba1b19d214bdc786a0e1952a441f3b5))

## v2.0.0 (2022-12-06)
### Feature
* Change object_name into a property that uses the model verbose_name_plural ([`c0e2206`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c0e2206178d886f27011bc70b111439a172c53c6))
### Breaking
* Removed object_name attr and instead made it a property  ([`c0e2206`](https://github.com/Centers-Health/dynamics-py-gfl/commit/c0e2206178d886f27011bc70b111439a172c53c6))

## v1.4.7 (2022-12-06)
### Fix
* Add back dispatch sidePanelLoad event ([`55650d7`](https://github.com/Centers-Health/dynamics-py-gfl/commit/55650d7089f348359276cd755dd70b87807da500))

## v1.4.6 (2022-11-30)
### Fix
* Recalculate frozen column widths on gfl table resize ([`a1b54b2`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a1b54b25dfb4d1be0a5357673370e7c899b427c5))

## v1.4.5 (2022-11-30)
### Fix
* Update dynpy-actions dependency (allow until next breaking change) ([`703775b`](https://github.com/Centers-Health/dynamics-py-gfl/commit/703775b4537e7bd9bc8d549269c8c45f518b1723))

## v1.4.4 (2022-11-29)
### Fix
* Use URLSearchParams when clearing filters ([`8ea4e01`](https://github.com/Centers-Health/dynamics-py-gfl/commit/8ea4e01f144064edd33e86fae86108fc879444dc))

## v1.4.3 (2022-11-23)
### Fix
* Update dynpy actions version ([`01cfc43`](https://github.com/Centers-Health/dynamics-py-gfl/commit/01cfc43cfee801db94d3ad1a6bd21aa47506319c))

## v1.4.2 (2022-11-22)
### Fix
* Check if btn exists before applying onclick ([`3c4b515`](https://github.com/Centers-Health/dynamics-py-gfl/commit/3c4b5159d60d11429da4e40dd0644ab6b0ed4815))

## v1.4.1 (2022-11-22)
### Fix
* Remove new line between ? and url ([`f4a8a48`](https://github.com/Centers-Health/dynamics-py-gfl/commit/f4a8a4846e8a4205e23eab6176f5cbbfc0423c41))

## v1.4.0 (2022-11-22)
### Feature
* Add "No Results Found" message if no results returned ([`8bdc720`](https://github.com/Centers-Health/dynamics-py-gfl/commit/8bdc7209e9807613e2e9c5eed00e1520747e1583))
* Scrolling enhancements ([`2054d6d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/2054d6d9541b6cdf0c9d52e4a515baacc4574a57))

## v1.3.0 (2022-11-10)
### Feature
* Add precommit check for migrations ([`9020d2e`](https://github.com/Centers-Health/dynamics-py-gfl/commit/9020d2e35bf54705e0321b1a7896459c8ae0eff1))

## v1.2.0 (2022-11-10)
### Feature
* Remove unnecessary br tag ([`d552a53`](https://github.com/Centers-Health/dynamics-py-gfl/commit/d552a53134317599699e84a3eab55e808c3c5231))
* Hide reset filters when none applied ([`a91f009`](https://github.com/Centers-Health/dynamics-py-gfl/commit/a91f0092763ce87cbafbb8eb6a79325c06525b48))
* Make filters collapsible ([`0ae2194`](https://github.com/Centers-Health/dynamics-py-gfl/commit/0ae2194984dfccec7f6bb4d1277855a7d92c1ce9))
### Fix
* Add names to end blocks ([`76d9fce`](https://github.com/Centers-Health/dynamics-py-gfl/commit/76d9fce06fdd652c22092a0cfdfd8c7bffd6c1b0))

## v1.1.0 (2022-11-08)
### Feature
* Add ability to freeze first `n` columns ([`6817f7c`](https://github.com/Centers-Health/dynamics-py-gfl/commit/6817f7c2cb80cdee798f57775e25b37d8b2be7ed))

## v1.0.0 (2022-11-07)
### Fix
* Remove quotes from table_row block ([`1080492`](https://github.com/Centers-Health/dynamics-py-gfl/commit/1080492eec63e0d876584b7a887f223b9f8cedae))
### Breaking
* breaks projects who override the table_row block  ([`1080492`](https://github.com/Centers-Health/dynamics-py-gfl/commit/1080492eec63e0d876584b7a887f223b9f8cedae))

## v0.3.1 (2022-11-03)
### Fix
* Set close_side_panel input in the JS ([`e04a62d`](https://github.com/Centers-Health/dynamics-py-gfl/commit/e04a62d1fde179205d74a3b8c83c519f083653e5))
* 🐛 Fix 'x' sometimes having an extra margin ([`9bd04d3`](https://github.com/Centers-Health/dynamics-py-gfl/commit/9bd04d340ea231a25f55be001b6241c67892b5df))

## v0.3.0 (2022-11-02)
### Feature
* Refactor side panel JS to handle close button ([`01d7570`](https://github.com/Centers-Health/dynamics-py-gfl/commit/01d7570f6dc06beb30815cf20962605e74b61908))
* Add styles for close button and a transition for closing the panel ([`21bf043`](https://github.com/Centers-Health/dynamics-py-gfl/commit/21bf0437be01e79a4f1d2a43236d7aff82ad4e23))
* Add in ability to have side panel closed by default ([`7d23595`](https://github.com/Centers-Health/dynamics-py-gfl/commit/7d2359597e4aae6ca8691e4f1bc3f3f671837092))
* Refactor split view template ([`5c4ae40`](https://github.com/Centers-Health/dynamics-py-gfl/commit/5c4ae40e6a89e43adc7e41bc52ab76b167f1b445))

## v0.2.0 (2022-11-01)
### Feature
* Fix minor version (update README) ([`5f3f4d4`](https://github.com/Centers-Health/dynamics-py-gfl/commit/5f3f4d4cb8a34223481beb8119b67c33681f112e))

## v0.1.1 (2022-10-21)
### Fix
* Modify dependency pinning in pyproject.toml ([`3fe0479`](https://github.com/Centers-Health/dynamics-py-gfl/commit/3fe0479363a2891b6b0944a1b52233ee081fcb68))

## v0.1.0 (2022-09-15)
### Feature
* Add flake8_baseline and ready for initial package ([`7394dd0`](https://github.com/Centers-Health/dynamics-py-gfl/commit/7394dd0479b167195e8a292975ff0c4c7319650f))
### Documentation
* Update readme ([`058099c`](https://github.com/Centers-Health/dynamics-py-gfl/commit/058099c2e3cdbae634aafb99f5e4657bd978d8a5))
