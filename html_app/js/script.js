let $name_input = $("#name_input");
let $add_btn = $("#add_btn");

let $requirement_container = $("#requirements_list_container");

$name_input.on('keypress',function(e) {
    if (e.which == 13) {
        $add_btn.click();
    }
});

$add_btn.click(function () {
    if ($name_input.val() !== "") {
        let $new_img, $new_text, $new_div;
        if ($name_input.val().endsWith(".mpy") || $name_input.val().endsWith(".py")) {
            $new_img = $('<img class="icon_img" src="img/file.png">');
        }else{
            $new_img = $('<img class="icon_img" src="img/folder.png">');
        }

        $new_text = $(`<input class="lib_input" type="text" value="${$name_input.val()}">`);

        $new_div = $('<div class="requirement_row"></div>');

        $new_indent_div = $('<div class="indent_2"></div>');
        $new_indent_div.append($new_img);
        $new_indent_div.append(" ");
        $new_indent_div.append($new_text);
        $new_div.append($new_indent_div);

        $requirement_container.append($new_div);
    }
});