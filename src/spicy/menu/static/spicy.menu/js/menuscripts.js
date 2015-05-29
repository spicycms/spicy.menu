var spicy_menu = {}

spicy_menu.init = function() {

   // this.li_url = $('li:has(label[for="id_url"])');

   // this.li_consumer = $('li:has(label[for="id_consumer"])')

   // this.input_url = $('input#id_url')

   // this.checkbox = $('input[type="checkbox"]')

    this.treediv = $('.tree');

    this.menu_slug = this.treediv.attr('data-menu-slug');



    this.checkSwitch = function() {

        //fix state of switch between url and consumer
        //on load if there's no consumer and url is checked

        var li_url = $('li:has(label[for="id_url"])');
        var li_consumer = $('li:has(label[for="id_consumer"])')
        var input_url = $('input#id_url')
        var checkbox = $('input[type="checkbox"]')
        if (input_url.val()) {
            checkbox.prop('checked', false);
            li_consumer.hide()
            li_url.show()
        }
    }


    this.moveslug = function() {

        //a little fix due to no decent verbatim template tag in django 1.4
        slug = $('.moveslug').html()
        $('.moveslug').remove()
        $('.slug').html('\''+slug+'\'')
    }


    this.get_preview = function() {

        //load preview of menu via ajax

        $.ajax({
            type: "GET",
            url: full_path_with_port + 'preview/',
            cache: false,
            async: false,
            success: function(data) {
                $('.preview').html(data);

            }
        });

    }

    this.subm_ajax_form = function(e, url) {

        //submit form via ajax
        //by default (without url) loads html from django request
        //with url parameter gets url from django copy view and redirects


        e.preventDefault();



        if (!url) { //decide if we add a loaded page to the right block or redirect to another menu
            url = $('#form_ajax').attr('action')
        } else {
            var refresh_page = true
        }



        $.ajax({
            type: "POST",
            url: url,
            data: $('#form_ajax').serialize(),

            success: function(data) {

                if (refresh_page) {
                    window.location = data; //from django copy view, redirect to the menu, where the node was copied to

                } else { //from other views

                    $('.entryedit').html(data);



                    spicy_menu.treediv.jstree("deselect_all"); //refresh tree with new data
                    spicy_menu.treediv.jstree(true).settings.core.data = spicy_menu.get_tree_json();
                    spicy_menu.treediv.jstree("refresh");

                    spicy_menu.initBootstrapSwitch();
                    spicy_menu.checkSwitch();
                    spicy_menu.get_preview();
                }
            }
        });

    }



    this.parseId = function(id) { //get django Menu Id and menuEntry Id for given node
        re = /\d+/g
        return id.match(re);
    }


    this.bindCopies = function() {

        ////sets callbacks for copying node to another menu

        $('.copylink').on('click', function(e) {
            e.preventDefault();
            url = $(e.target).attr('href');
            spicy_menu.subm_ajax_form(e, url);
        });
    }


    this.get_tree_json = function() {

        // gets json needed to init menu's jstree

        var myjson;
        $.ajax({
            type: "GET",
            url: host_with_port + '/admin/menu/ajax_list/' + this.menu_slug + '/',
            dataType: "json",
            cache: false,
            async: false,
            success: function(data) {
                myjson = data;

            }
        });
        return myjson
    }

    this.initjstree = function() {

        //inits jstree and binds all the callbacks


        this.treediv.jstree({

            'core': {
                'data': this.get_tree_json(),
                'check_callback': function(operation, node, node_parent, node_position, more) {

                    // operation can be 'create_node', 'rename_node', 'delete_node', 'move_node' or 'copy_node'
                    // in case of 'rename_node' node_position is filled with the new node name

                    if (operation === "move_node") {
                        return (node_parent.id != '#'); //only allow dropping inside nodes of type 'Parent'
                    }
                    return true; //allow all other operations
                }

            },
            'plugins': ["dnd"]
        }).on("move_node.jstree", function(e, data) { //sends POST request to django to move node
            if (!data.position) {
                data.position = 0
            }
            console.log(data.position)
            $.ajax({
                type: "POST",
                dataType: 'json',
                url: host_with_port + '/admin/menu/entries/' + spicy_menu.parseId(data.node.id)[1] + '/move/',
                data: {
                    "parent": spicy_menu.parseId(data.node.parent)[1],
                    "position": data.position+1,
                    "menu": spicy_menu.parseId(data.node.parent)[0]
                },
                success: function() {
                 spicy_menu.get_preview();
            }

            });



        }).on("select_node.jstree", function(evt, data) { //opens block with a form (and related object info) on node select

            var url, checkbox;

            if (spicy_menu.parseId(data.node.id).length > 1) {

                spicy_menu.loadEditor(host_with_port + '/admin/menu/entries/' + spicy_menu.parseId(data.node.id)[1] + '/');


                if (data.node.original.consumer) {  //related object (consumer) info
                    $('.plugin').removeClass('hide')
                    $('.linked').html('<a class="btn btn-default" href="' + data.node.original.consumer.url + '"><i class="icon icon-eye-open"></i> Смотреть связанный объект на сайте</a> <a class="btn btn-default" href="' + data.node.original.consumer.admin_url + '"><i class="icon icon-pencil"> </i>Редактировать связанный объект</a>')
                    $('.consumer_title').html('Связанный объект: ' + data.node.original.consumer.title)
                } else {
                    $('.plugin').addClass('hide')
                }

                //spicy_menu.checkSwitch()

            }
        });
    }

    this.initBootstrapSwitch = function() {

        //init switch widget for selecting between an object (consumer) and url
        //in entry edit form

        var input_url = $('input#id_url')
        if (!input_url.val()) {
            $('li:has(label[for="id_url"])').val('').hide();
        }

        $("[name='my-checkbox']").bootstrapSwitch().on(
            "switch-change", function(e, data) {
                var li_url = $('li:has(label[for="id_url"])');
                var li_consumer = $('li:has(label[for="id_consumer"])')
                var checkbox = $("[name='my-checkbox']")
                if (checkbox.prop('checked')) {
                    input_url.val('')

                    li_url.hide();
                    li_consumer.show();
                } else {

                    if ($('.deck').children().length > 0) {
                        var widget = $('.autocomplete-light-widget').yourlabsWidget();
                        var choice;
                        if ($('.deck>.div').length) {
                            choice = $('.deck>.div')
                        } else if ($('.hilight').length) {
                            choice = $('.hilight')
                        }

                        widget.deselectChoice(choice);

                    }

                    li_url.show();
                    li_consumer.hide();


                }
            }
        );

        $('body').on('click', '.autocomplete-light-widget .deck .remove', function() {
            $('.plugin').addClass('hide'); //hide block on deselecting choice in autocomplete
        });
    }

    this.loadEditor = function(url) {

        //loads given url in right block

        $.ajax({
            type: "GET",
            url: url,
            async: false,
            success: function(data) {
                $('.entryedit').html(data);
                spicy_menu.initBootstrapSwitch();
            }
        });

    }

    this.init_loaded_page = function() { //initialize scripts on a page loaded via ajax

         $("form#form_ajax").submit(function(e) {

                spicy_menu.subm_ajax_form(e);

            });

            spicy_menu.checkSwitch()

            spicy_menu.bindCopies()
    }

    this.bind_add_menu_entry_button = function() {

      //makes add menu entry button work

        $('.add_menu_entry').on('click', function(e) {
            e.preventDefault();
            current_menu_id = $('.tree').attr('data-menu-id')
            // $("#tree").jstree("deselect_all");
            spicy_menu.loadEditor(host_with_port + '/admin/menu/entries/add/?menu=' + current_menu_id)
            $("form#form_ajax").submit(function(e) {
                alert = '<div class="padded"><div class="alert">Пункт меню успешно создан</div></div>'
                current_menu_id = $('.tree').attr('data-menu-id')
                $("#id_menu").val(current_menu_id)
                spicy_menu.subm_ajax_form(e, false);

            });



        });
    }

}


$(function() {

    spicy_menu.init()
    spicy_menu.moveslug()
    spicy_menu.initjstree()
    spicy_menu.get_preview()
    spicy_menu.bind_add_menu_entry_button()

});
