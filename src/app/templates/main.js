(() => {
    // prevent form to be submitted by clicking on the print button
    $("#print").click((e) => e.preventDefault());

    let debouncePreviewTimeout = false;

    const Modes = {
        Image: "image",
        QrCode: "qrcode",
        Text: "text",
    };

    function clamp(min, number, max) {
        if (number < min) {
            return min;
        }
        if (number > max) {
            return max;
        }
        return number;
    }

    function get_mode() {
        return $("#mode:checked").val();
    }

    function updateMode() {
        switch (get_mode()) {
            case Modes.QrCode:
                $("#card_label_text").hide();
                $("#card_label_image").hide();
                $("#card_font_format").hide();
                $("#card_label_qrcode").show();
                break;
            case Modes.Image:
                $("#card_label_qrcode").hide();
                $("#card_label_text").hide();
                $("#card_font_format").hide();
                $("#card_label_image").show();
                break;
            case Modes.Text:
                $("#card_label_qrcode").hide();
                $("#card_label_image").hide();
                $("#card_font_format").show();
                $("#card_label_text").show();
                break;
        }
        preview();
    }

    function buildRequestBody() {
        const mode = get_mode();
        const formData = new FormData();
        formData.append("label_size", $("#label_size").find(":selected").val());
        formData.append(
            "orientation",
            $("input[name='label_orientation']:checked").val(),
        );

        if (mode === Modes.Image) {
            formData.append("file", $("#label_image")[0].files[0]);
        }
        if (mode === Modes.QrCode || mode === Modes.Text) {
            formData.append(
                "margin_left",
                clamp(0, $("#margin_left").val(), 255),
            );
            formData.append(
                "margin_right",
                clamp(0, $("#margin_right").val(), 255),
            );
            formData.append(
                "margin_top",
                clamp(0, $("#margin_top").val(), 255),
            );
            formData.append(
                "margin_bottom",
                clamp(0, $("#margin_bottom").val(), 255),
            );

        }
        if (mode === Modes.QrCode) {
            formData.append("qr_text", $("#qr_text").val());
            formData.append(
                "error_correction",
                $("#qr_error").find(":selected").val(),
            );
            formData.append(
                "qr_align",
                $("input[name='qr_align']:checked").val(),
            );
        }
        if (mode === Modes.Text) {
            formData.append(
                "font_name",
                $("#font_family").find(":selected").text(),
            );
            formData.append("font_size", clamp(3, $("#font_size").val(), 255));
            formData.append("text", $("#label_text").val() || " ");
            formData.append(
                "valign",
                $("input[name='font-vertical-align']:checked").val(),
            );
            formData.append(
                "halign",
                $("input[name='font-horizontal-align']:checked").val(),
            );
            formData.append(
                "underline",
                $("#font_style_underline:checked").val() === "underline",
            );
            formData.append(
                "orientation",
                $("input[name='label_orientation']:checked").val(),
            );
            formData.append(
                "font_spacing",
                clamp(0, $("#font_spacing").val(), 255),
            );
        }
        return formData;
    }

    function preview() {
        if (debouncePreviewTimeout) clearTimeout(debouncePreviewTimeout);
        debouncePreviewTimeout = setTimeout(() => {
            $.ajax({
                // jquery needs these two settings when passing in a FormData instance
                processData: false,
                contentType: false,
                type: "post",
                url: "/preview",
                data: buildRequestBody(),
                success: (result) => {
                    $("#preview").attr(
                        "src",
                        `data:image/png;base64,${result}`,
                    );
                },
            });
        }, 300);
    }

    function printLabel() {
        $("#status")
            .html("printing...")
            .removeClass(
                "alert-info alert-danger alert-warning alert-success alert-secondary",
            )
            .addClass("alert-info");

        $.ajax({
            processData: false,
            contentType: false,
            type: "post",
            url: "/print",
            data: buildRequestBody(),
            success: (result) => {
                $("#status")
                    .html(result[1])
                    .removeClass(
                        "alert-info alert-danger alert-warning alert-success alert-secondary",
                    )
                    .addClass(result[0]);
            },
            error: (result) => {
                $("#status")
                    .html(
                        `<b>E R R O R</b>The API threw an error!<b>Status:</b>${result.status}<b>Info:</b>${result.responseText}`,
                    )
                    .removeClass(
                        "alert-info alert-danger alert-warning alert-success",
                    )
                    .addClass("alert-danger");
                console.warn(
                    `The API returned the status code ${result.status}`,
                );
                console.warn(
                    `The API gave these additional information: ${result.responseText}`,
                );
            },
        });
    }

    $(document).ready(() => {
        updateMode();
        preview();
        $("#label_image").on("change", () => preview());
    });

    $("#font_family").change(() => preview());
    $("#label_size").change(() => preview());
    $("#label_text").keyup(() => preview());
    $("#font_size").change(() => preview());
    $("#font_size").keyup(() => preview());
    $("input[name='font-vertical-align']").change(() => preview());
    $("input[name='font-horizontal-align']").change(() => preview());
    $("input[name='label_orientation']").change(() => preview());
    $("input[name='mode']").change(() => updateMode());
    $("#qr_text").keyup(() => preview());
    $("#qr_error").change(() => preview());
    $("#margin_left").change(() => preview());
    $("#margin_right").change(() => preview());
    $("#margin_top").change(() => preview());
    $("#margin_bottom").change(() => preview());
    $("#font_spacing").change(() => preview());
    $("#qr_align_center").change(() => preview());
    $("#qr_align_left").change(() => preview());
    $("#qr_align_right").change(() => preview());
    $("#print_label").click(() => printLabel());
})();
