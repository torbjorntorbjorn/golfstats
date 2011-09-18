"use strict";

// Development helper
$(function() {
    var button = $("<button></button>", {
        text: "debug: fill scorecard",
        click: function(e) {
            $("#scorecard input.ob_throws").val(0);
            $("#scorecard input.throws").val(3).change();
        }
    }).appendTo("section:first");
});

// Handles result row, scores and changes to
// score elements
$(function() {
    var scorecard = $("#scorecard");

    // matrix with players, courseholes and scores
    var scores = {};

    // Holds DOM references to each players result cell
    var result_cells = {};

    // Find all players and make scores variable
    var player_ids = [];
    scorecard.find("thead th").each(function(i, el) {
        player_ids.push($(el).data("player_id"));
    });

    // Find all holes and record ids
    var courseholes_ids = [];
    scorecard.find("tbody tr").each(function(i, el) {
        courseholes_ids.push($(el).data("coursehole_id"));
    });

    // Initialize all scores to 0
    $(player_ids).each(function(i, player_id) {
        scores[player_id] = {};

        $(courseholes_ids).each(function(j, ch_id) {
            scores[player_id][ch_id] = 0;
        });
    });

    // Create and insert result row
    (function() {
        var score_row = $("<tr></tr>");
        score_row.append($("<td>Scores</td>"));

        for (var player_id in scores) {
            var result_cell = $("<td>0</td>");
            result_cells[player_id] = result_cell.get(0);
            score_row.append(result_cell);
        }
        scorecard.find("thead").append(score_row);
    })();

    // Sum player and update result cell
    function sum_player(player_id) {
        var score = 0;
        var player_scores = scores[player_id];

        for (var ch_id in player_scores) {
            score += player_scores[ch_id];
        }

        result_cells[player_id].innerHTML = score;
    }

    // Maintain score object, and possibly sum affected player
    function score_change(el, do_sum) {
        var do_sum = do_sum || false;

        var el = $(el);

        if (!el.val().match(/^\d+$/)) {
            // Element value not an integer
            return;
        }

        // Hmf, 'throws' is a keyword
        var _throws = parseInt(el.val(), 10);

        var player_id = el.parents("td").data("player_id");
        var ch_id = el.parents("tr").data("coursehole_id");
        var par = el.parents("tr").data("coursehole_par");

        // Set the score
        scores[player_id][ch_id] = _throws - par;

        // Update result cell
        if (do_sum) {
            sum_player(player_id);
        }
    }

    // Init score object and capture change event
    scorecard.find("tbody input.throws").each(function(i, el) {
        // Connect event handlers
        $(el).bind("change keyup click", function(e) {
            score_change(e.currentTarget, true);
        });

        // Initial scores
        score_change(el);
    });

    // Run sum_player for all players
    $(player_ids).each(function(i, player_id) {
        sum_player(player_id);
    });
});

// Handles dialog on scorecard clicks
$(function() {
    var scorecard = $("#scorecard");

    // Set up dialog
    var dialog = $("#score-dialog");
    var dialog_throws = $("#dialog-throws");
    var dialog_ob_throws = $("#dialog-ob_throws");

    dialog.css("display", null);
    dialog.dialog({
        autoOpen: false,
        height: "auto",
        modal: true,
        center: true,
        width: 560
    });

    // Update cell text with scores
    function paint_cell(_throws, _ob_throws, cell_text) {
        // Empty cell if no throws
        if (_throws == "") {
            cell_text.html("");
            return;
        }

        // Output string
        var content = _throws;

        if (_ob_throws && _ob_throws != 0) {
            // Ugh, ugly string formatting
            // TODO: Pull in underscore.js strings or something ?
            content = content + " (" + _ob_throws + ")";
        }

        cell_text.html(content);
    }

    // Maps names to selector meta-objects
    // The meta-objects describe a row selector buttons
    var selector_names = {
        "throws": {
            "selector": $("#throws-selector li"),
            "adjust_val": -2
        },

        "ob_throws": {
            "selector": $("#ob_throws-selector li"),
            "adjust_val": 0
        }
    };

    // Update which button is active
    function update_selector(name, val) {
        var current =  selector_names[name];
        var els = current.selector;

        // Value comes straigt from input element content,
        // needs to be shited to be used as index
        var val = parseInt(val, 10) + current.adjust_val;

        // Valus is higher than length or buttons, or below 0,
        // so we just disable all buttons and return
        if (val > els.length || val < 0) {
            els.removeClass("active");
            return;
        }

        var selected = $(els.get(val));
        // If the selected element is not currently selectd,
        // disable all buttons and set the right one as selected
        if (!selected.hasClass("active")) {
            els.removeClass("active");
            selected.addClass("active");
        }
    }

    // Bind the dialog input elements to the selector buttons,
    // so that the buttons are correct when 
    // changing the input element directly.
    $.each({
        "throws": dialog_throws,
        "ob_throws": dialog_ob_throws

    }, function(name, el) {
        // Call update_selector on all changes to input element
        el.bind("change keyup click", function(e) {
            update_selector(name, el.val());
        });
    });

    // Handle click event and dialog usage
    scorecard.find("tbody td").each(function(i, el) {
        var el = $(el);
        var el_throws = el.find("input.throws");
        var el_ob_throws = el.find("input.ob_throws");

        // Hide cell contents
        el.contents().css("display", "none");

        // Create and append our own output field
        var cell_text = $("<p></p>");
        el.append(cell_text);

        // Draw our cell usage the data already
        // in the elements
        paint_cell(el_throws.val(), el_ob_throws.val(), cell_text);

        el.click({
            dialog: dialog,
            dialog_throws: dialog_throws,
            dialog_ob_throws: dialog_ob_throws,
            el: el,
            el_throws: el_throws,
            el_ob_throws: el_ob_throws,
            cell_text: cell_text
        }, function(el_click) {

            // Trigger on dialog open
            dialog.bind("dialogopen", {
                el: el_click.data.el,
                el_throws: el_click.data.el_throws,
                el_ob_throws: el_click.data.el_ob_throws
            }, function(dialog_open, ui) {

                // Shorthand for event element
                var e = dialog_open;

                // Set values on dialog input elements
                dialog_throws.val(e.data.el_throws.val());
                dialog_ob_throws.val(e.data.el_ob_throws.val());

                // Update dialog selectors
                update_selector("throws", e.data.el_throws.val());
                update_selector("ob_throws", e.data.el_ob_throws.val());

                // Set title on dialog
                dialog.dialog("option", "title", e.data.el.data("player_name"));
            });

            // Dialog buttons
            dialog.dialog("option", "buttons", {
                "Cancel": function(e) {
                    dialog.dialog("close");
                },

                "OK": function(e) {
                    // Close over click_data
                    return (function(click_data) {
                        // Shorthand for click event data
                        var e = click_data;

                        // Set values back on scorecard
                        e.el_throws.val(e.dialog_throws.val());
                        e.el_ob_throws.val(e.dialog_ob_throws.val());

                        // Trigger change event on throws element
                        e.el_throws.change();

                        // Update cell with new values
                        paint_cell(e.el_throws.val(), e.el_ob_throws.val(),
                            e.cell_text);

                        dialog.dialog("close");
                    })(el_click.data);
                }
            });

            // Actually open the dialog
            dialog.dialog("open");
        });
    });

    // Connect selectors to elements
    var selector_clicks = [
        [selector_names["throws"], dialog_throws],
        [selector_names["ob_throws"], dialog_ob_throws]
    ];

    // Generic handling of selector button clicks
    $.each(selector_clicks, function(i, tuple) {
        var current = tuple[0]; // selector metaobject
        var el = tuple[1]; // dialog input element

        // Clicking on a selector button updates
        // the dialog input element
        current.selector.live('click', function(e) {
            el.val(e.target.innerHTML);

            var t = $(e.target);
            t.siblings().removeClass("active");
            t.addClass("active");
        });
    });
});
