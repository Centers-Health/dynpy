/**
 * jQuery Formset 1.5-pre
 * @author Stanislaus Madueke (stan DOT madueke AT gmail DOT com)
 * @requires jQuery 1.2.6 or later
 *
 * Copyright (c) 2009, Stanislaus Madueke
 * All rights reserved.
 *
 * Licensed under the New BSD License
 * See: http://www.opensource.org/licenses/bsd-license.php
 */
(function ($) {
  $.fn.formset = function (opts) {
    const options = $.extend({}, $.fn.formset.defaults, opts),
      wrapper = $(this).parent(),
      flatExtraClasses = options.extraClasses.join(" "),
      totalForms = $("#id_" + options.prefix + "-TOTAL_FORMS", wrapper),
      maxForms = $("#id_" + options.prefix + "-MAX_NUM_FORMS", wrapper),
      minForms = $("#id_" + options.prefix + "-MIN_NUM_FORMS", wrapper),
      childElementSelector = "input,select,textarea,label,div",
      $$ = $(this);
    const removeLastAddForm =
      options.removeLastAddForm ||
      (options.removeLastAddFormUnlessIsOnlyForm && totalForms.val() > 1);
    const applyExtraClasses = function (row, ndx) {
        if (options.extraClasses) {
          row.removeClass(flatExtraClasses);
          row.addClass(options.extraClasses[ndx % options.extraClasses.length]);
        }
      },
      refreshAddText = function () {
        const addButton = $(`#${options.prefix}_add_btn`, wrapper);
        const itemName = $(options.itemName, wrapper)
          ? `${options.itemName}`
          : "";
        const forms = $("." + options.formCssClass, wrapper).not(":hidden");
        if (forms.length < 1) {
          addButton.html(`${options.addTextWhenEmpty} ${itemName}`);
        } else {
          addButton.html(`${options.addText} ${itemName}`);
        }
      },
      addRow = function (row, buttonRow, formCount) {
        scripts = row.find("script").clone(true);
        row.find("script").remove();
        row.find(childElementSelector).each(function () {
          updateElementIndex($(this), options.prefix, formCount);
          if (options.showLabelsOnce) $(this).find("label").remove();
        });

        row.insertBefore(buttonRow).show();
        const inputPrefix = `${options.prefix}-${formCount}`;
        const input = $(`[name*=${inputPrefix}]`, wrapper)[0];
        scripts.each(function () {
          updateElementIndex($(this), options.prefix, formCount);
          var script = document.createElement("script");
          script.type = "text/javascript";
          script.textContent = $(this).text();
          script.id = $(this).attr("id");
          input.parentElement.append(script);
        });
      },
      getFormTemplate = function () {
        let template;
        if (options.formTemplate) {
          // If a form template was specified, we'll clone it to generate new form instances:
          template =
            options.formTemplate instanceof $
              ? options.formTemplate
              : $(options.formTemplate);
          template.addClass(options.formCssClass + " formset-custom-template");
          insertDeleteLink(template);
        } else {
          // Otherwise, use the last form in the formset
          template = $("." + options.formCssClass + ":last", wrapper).clone(
            true
          );
          template.find('input:hidden[id $= "-DELETE"]').remove();
          // Clear all cloned fields, except those the user wants to keep (thanks to brunogola for the suggestion):
          template
            .find(childElementSelector)
            .not(options.keepFieldValues)
            .each(function () {
              var elem = $(this);
              // If this is a checkbox or radiobutton, uncheck it.
              // This fixes Issue 1, reported by Wilson.Andrew.J:
              if (elem.is("input:checkbox") || elem.is("input:radio")) {
                elem.attr("checked", false);
              } else {
                elem.val("");
              }
            });
        }
        template.removeAttr("id");
        template.find(childElementSelector).each(function () {
          updateElementIndex($(this), options.prefix, "__prefix__");
        });
        return template;
      },
      setAttrsOnChange = function (row) {
        // In order to keep values when cloning, we need to update the corresponding attributes in the DOM
        // when the user changes the input.
        function updateAttributes(e) {
          // Get the value from the input element
          const inputElement = e.target;
          const inputValue = $(inputElement).val();

          // Handle different input types
          switch (inputElement.type) {
            case "select-one":
              // For select elements, set the 'selected' attribute for the chosen option
              const selectOneOptions = $(inputElement).find("option");
              selectOneOptions.each(function () {
                if ($(this).val() === inputValue) {
                  $(this).attr("selected", "selected");
                } else {
                  $(this).removeAttr("selected");
                }
              });
              break;

            case "select-multiple":
              // For multi-select elements, set the 'selected' attribute for the chosen options
              const selectedValues = $(inputElement).val();
              const selectMultiOptions = $(inputElement).find("option");

              selectMultiOptions.each(function () {
                if (selectedValues.includes($(this).val())) {
                  $(this).attr("selected", "selected");
                } else {
                  $(this).removeAttr("selected");
                }
              });
              break;

            case "checkbox":
            case "radio":
              // For checkboxes and radio buttons, set the 'checked' attribute based on the state
              if ($(inputElement).prop("checked")) {
                $(inputElement).attr("checked", "checked");
              } else {
                $(inputElement).removeAttr("checked");
              }
              break;

            case "file":
              // For file inputs, you cannot set the 'value' attribute directly
              // Not handling this case because you generally don't want to pre-fill file inputs
              break;

            default:
              // For other input types, set the 'value' attribute to the input value
              $(inputElement).attr("value", inputValue);
              break;
          }
        }
        row.find(childElementSelector).each(function () {
          $(this).change(updateAttributes);
        });
      },
      updateElementIndex = function (elem, prefix, ndx) {
        var idRegex = new RegExp(prefix + "-(\\d+|__prefix__)-"),
          replacement = prefix + "-" + ndx + "-";
        if (elem.attr("for"))
          elem.attr("for", elem.attr("for").replace(idRegex, replacement));
        if (elem.attr("id"))
          elem.attr("id", elem.attr("id").replace(idRegex, replacement));
        if (elem.attr("name"))
          elem.attr("name", elem.attr("name").replace(idRegex, replacement));
        if (elem.prop("tagName") === "SCRIPT")
          elem.text(elem.text().replace(idRegex, replacement));
      },
      hasChildElements = function (row) {
        return row.find(childElementSelector).length > 0;
      },
      showAddButton = function () {
        return (
          maxForms.length == 0 || // For Django versions pre 1.2
          maxForms.val() == "" ||
          maxForms.val() - totalForms.val() > 0
        );
      },
      /**
       * Indicates whether delete link(s) can be displayed - when total forms > min forms
       */
      showDeleteLinks = function () {
        return (
          minForms.length == 0 || // For Django versions pre 1.7
          minForms.val() == "" ||
          (totalForms.val() - minForms.val() > 0 && options.canDelete)
        );
      },
      insertDeleteLink = function (row) {
        var delCssSelector = $.trim(options.deleteCssClass).replace(
            /\s+/g,
            "."
          ),
          addCssSelector = $.trim(options.addCssClass).replace(/\s+/g, ".");

        var delButtonHTML =
          '<a class="' +
          options.deleteCssClass +
          '" >' +
          options.deleteText +
          "</a>";
        if (options.deleteContainerClass) {
          // If we have a specific container for the remove button,
          // place it as the last child of that container:
          row
            .find('[class*="' + options.deleteContainerClass + '"]')
            .append(delButtonHTML);
        } else if (row.is("TR")) {
          // If the forms are laid out in table rows, insert
          // the remove button into the last table cell:
          row.children(":last").append(delButtonHTML);
        } else if (row.is("UL") || row.is("OL")) {
          // If they're laid out as an ordered/unordered list,
          // insert an <li> after the last list item:
          row.append("<li>" + delButtonHTML + "</li>");
        } else {
          // Otherwise, just insert the remove button as the
          // last child element of the form's container:
          row.append(delButtonHTML);
        }

        // Check if we're under the minimum number of forms - not to display delete link at rendering
        if (!showDeleteLinks()) {
          row.find("a." + delCssSelector).hide();
        }

        row.find("a." + delCssSelector).click(function () {
          var row = $(this).parents("." + options.formCssClass),
            del = row.find('input:hidden[id $= "-DELETE"]'),
            buttonRow = row.siblings(
              "a." + addCssSelector + ", ." + options.formCssClass + "-add"
            ),
            forms;
          var deleteLabel = options.itemName
            ? `Delete ${options.itemName}`
            : `Delete`;
          bootbox.confirm({
            message: options.confirmationMessage,
            centerVertical: true,
            buttons: {
              confirm: {
                label: deleteLabel,
                className: "btn-primary btn-sm",
              },
              cancel: {
                className: "btn-secondary btn-sm",
              },
            },
            callback: function (result) {
              if (result === true) {
                if (del.length) {
                  // We're dealing with an inline formset.
                  // Rather than remove this form from the DOM, we'll mark it as deleted
                  // and hide it, then let Django handle the deleting:
                  del.val("on");
                  row.hide();
                  forms = $("." + options.formCssClass, wrapper).not(":hidden");
                  // If hiding last form, then can't subtract from totalForms.
                  // If subtract, it won't delete it.
                  if (!removeLastAddForm) {
                    totalForms.val(forms.length);
                  }
                } else {
                  row.remove();
                  // Update the TOTAL_FORMS count:
                  forms = $("." + options.formCssClass, wrapper).not(
                    ".formset-custom-template"
                  );
                  totalForms.val(forms.length);
                }
                for (var i = 0, formCount = forms.length; i < formCount; i++) {
                  // Apply `extraClasses` to form rows so they're nicely alternating:
                  applyExtraClasses(forms.eq(i), i);
                  if (!del.length) {
                    // Also update names and IDs for all child controls (if this isn't
                    // a delete-able inline formset) so they remain in sequence:
                    forms
                      .eq(i)
                      .find(childElementSelector)
                      .each(function () {
                        updateElementIndex($(this), options.prefix, i);
                      });
                  }
                }
                // Check if we've reached the minimum number of forms - hide all delete link(s) in this formset
                if (!showDeleteLinks()) {
                  $$.parent()
                    .find("a." + delCssSelector)
                    .each(function () {
                      $(this).hide();
                    });
                }
                // Check if we need to show the add button:
                if (buttonRow.is(":hidden") && showAddButton())
                  buttonRow.show();
                // If a post-delete callback was provided, call it with the deleted form:
                if (options.removed) {
                  let fn = window[options.removed];
                  fn(row);
                }
                refreshAddText();

                // Remove header row
                const formsetHeader = $(`#header_${options.id}`, wrapper)[0];
                if (options.showHeaderRow && forms.length === 0) {
                  formsetHeader.classList.add("d-none");
                }
              }
            },
          });
        });
      };

    $$.each(function (i) {
      var row = $(this),
        del = row.find('input:checkbox[id $= "-DELETE"]');

      setAttrsOnChange(row);

      if (del.length) {
        // If you specify "can_delete = True" when creating an inline formset,
        // Django adds a checkbox to each form in the formset.
        // Replace the default checkbox with a hidden field:
        if (del.is(":checked")) {
          // If an inline formset containing deleted forms fails validation, make sure
          // we keep the forms hidden (thanks for the bug report and suggested fix Mike)
          del.before(
            '<input type="hidden" name="' +
              del.attr("name") +
              '" id="' +
              del.attr("id") +
              '" value="on" />'
          );
          row.hide();
        } else {
          del.before(
            '<input type="hidden" name="' +
              del.attr("name") +
              '" id="' +
              del.attr("id") +
              '" />'
          );
        }
        // Hide any labels associated with the DELETE checkbox:
        $('label[for="' + del.attr("id") + '"]', wrapper).hide();
        del.remove();
      }
      if (hasChildElements(row)) {
        row.addClass(options.formCssClass);
        insertDeleteLink(row);
        applyExtraClasses(row, i);
      }
    });
    let rowTemplate = getFormTemplate();
    if ($$.length) {
      var hideAddButton = !showAddButton(),
        addButton;
      const itemName = options.itemName ? options.itemName : "";
      let addButtonHTML = `<a id="${options.prefix}_add_btn" class="${options.addCssClass}" href="javascript:void(0)">${options.addText} ${itemName}</a>`;

      if (removeLastAddForm) {
        // Remove last form
        $("." + options.formCssClass + ":last", wrapper).hide();
        totalForms.val(parseInt(totalForms.val()) - 1);

        // Change text of add button if no forms
        const forms = $("." + options.formCssClass, wrapper).not(":hidden");
        if (forms.length < 1) {
          addButtonHTML = `<a id="${options.prefix}_add_btn" class="${options.addCssClass}" href="javascript:void(0)">${options.addTextWhenEmpty} ${itemName}</a>`;
        }
      }

      if (options.addContainerClass) {
        // If we have a specific container for the "add" button,
        // place it as the last child of that container:
        var addContainer = $(
          '[class*="' + options.addContainerClass + '"',
          wrapper
        );
        addContainer.append(addButtonHTML);
        addButton = addContainer.find('[class="' + options.addCssClass + '"]');
      } else if ($$.is("TR")) {
        // If forms are laid out as table rows, insert the
        // "add" button in a new table row:
        var numCols = $$.eq(0).children().length, // This is a bit of an assumption :|
          buttonRow = $(
            '<tr><td colspan="' + numCols + '">' + addButtonHTML + "</tr>"
          ).addClass(options.formCssClass + "-add");
        $$.parent().append(buttonRow);
        addButton = buttonRow.find("a");
      } else {
        // Otherwise, insert it immediately after the last form:
        $$.filter(":last").after(addButtonHTML);
        addButton = $$.filter(":last").next();
      }

      if (hideAddButton) addButton.hide();
      if (removeLastAddForm) {
        // Remove hidden forms
        $$.filter(":hidden").remove();
      }

      addButton.click(function () {
        var formCount = parseInt(totalForms.val()),
          buttonRow = $(
            $(this)
              .parents("tr." + options.formCssClass + "-add")
              .get(0) || this
          ),
          delCssSelector = $.trim(options.deleteCssClass).replace(/\s+/g, ".");

        if (!removeLastAddForm || (removeLastAddForm && formCount > 0)) {
          rowTemplate = getFormTemplate();
        }

        applyExtraClasses(rowTemplate, formCount);
        addRow(rowTemplate, buttonRow, formCount);
        totalForms.val(formCount + 1);
        // Check if we're above the minimum allowed number of forms -> show all delete link(s)
        if (showDeleteLinks()) {
          $$.parent()
            .find("a." + delCssSelector)
            .each(function () {
              $(this).show();
            });
        }
        // Check if we've exceeded the maximum allowed number of forms:
        if (!showAddButton()) buttonRow.hide();
        // If a post-add callback was supplied, call it with the added form:
        if (options.added) {
          let fn = window[options.added];
          fn(rowTemplate);
        }
        refreshAddText();

        // Show header row
        const formsetHeader = document.querySelector(`#header_${options.id}`);
        if (options.showHeaderRow && formCount === 0) {
          formsetHeader.classList.remove("d-none");
        }

        return false;
      });
    }

    return $$;
  };

  /* Setup plugin defaults */
  $.fn.formset.defaults = {
    prefix: "form", // The form prefix for your django formset
    formTemplate: null, // The jQuery selection cloned to generate new form instances
    addText: '<i class="fa fa-plus"></i> Add another', // Text for the add link
    addTextWhenEmpty: '<i class="fa fa-plus"></i> Add a', // Text for the add link when there are no rows
    deleteText: "remove", // Text for the delete link
    addContainerClass: null, // Container CSS class for the add link
    deleteContainerClass: null, // Container CSS class for the delete link
    addCssClass: "add-row", // CSS class applied to the add link
    deleteCssClass: "delete-row", // CSS class applied to the delete link
    formCssClass: "dynamic-form", // CSS class applied to each form in a formset
    extraClasses: [], // Additional CSS classes, which will be applied to each form in turn
    keepFieldValues: "", // jQuery selector for fields whose values should be kept when the form is cloned
    added: null, // Function called each time a new form is added, can be a function or string of function name
    removed: null, // Function called each time a form is deleted, can be a function or string of function name
    removeLastAddForm: false, // When set to true, removes last empty add form
    removeLastAddFormUnlessIsOnlyForm: false, // When set to true, removes last empty add form, unless it's the only form
    itemName: null, // Used as label for item in bootbox confirm dialog
    canDelete: null, // When false, cannot delete a row
    showLabelsOnce: false, // When true, does not clone labels when adding new rows
    confirmationMessage: "Are you sure?", // Confirmation message for deleting rows
    id: null,
    showHeaderRow: false,
  };
})(jQuery);
