var ui_dropdown_menu = {
    init : function () {
        ui_dropdown_menu.instance.prototype = {
            init_events : function() {
                var obj = this;
                obj.dd.on('click', function(event){
                    console.log("yay");
                    $(this).toggleClass('active');
                    event.stopPropagation();
                });
                obj.opts.on('click',function(){
                    console.log("onclick");
                    var opt = $(this);
                    obj.val = opt.text();
                    obj.index = opt.index();
                    obj.placeholder.text('Gender: ' + obj.val);
                });
            },
            get_value : function() {
                return this.val;
            },
            get_index : function() {
                return this.index;
            },
            add_entry(name, data) {
                this.dd.append(
                    '<li><a href="#">' + name + '</a></li>'
                );
                this.opts = this.dd.find('ul.dropdown > li');
            },
            clear : function () {

            }
        }
        $(document).click(function() {
            $('.wrapper-dropdown').removeClass('active');
        });
    },
    create : function (id) {
        var instance = new ui_dropdown_menu.instance( $('#'+id) );
        return instance;
    },
    instance : function (el) {
        this.dd = el;
        this.placeholder = this.dd.children('span');
        this.opts = this.dd.find('ul.dropdown > li');
        this.val = '';
        this.index = -1;
        this.init_events();
    }
}


class ContextMenu {

    constructor(contextMenuId, // id attribute of the context menu
                //taskItemClassName, // class of the elements that should open the contextmenu
                filterFunction, // takes a dom node as input and return a boolean. Indicates if the dom node should have this context menu
                item_list, // [ { "name", "class", "action" } ... ] of the menu entries, name is shown as title, class is added to the classlist,
                           // action is a function taking a dom node which is called once the item of the context menu is clicked
                contextMenuClassName = "ui-context-menu",
                contextMenuUlClassName = "ui-context-menu__items",
                contextMenuItemClassName = "ui-context-menu__item",
                contextMenuLinkClassName = "ui-context-menu__link",
                contextMenuActiveClassName = "ui-context-menu--active") {

        //this.taskItemClassName = taskItemClassName;
        this.filterFunction = filterFunction;
        this.item_list = item_list;
        this.contextMenuClassName = contextMenuClassName;
        this.contextMenuUlClassName = contextMenuUlClassName;
        this.contextMenuItemClassName = contextMenuItemClassName;
        this.contextMenuLinkClassName = contextMenuLinkClassName;
        this.contextMenuActiveClassName = contextMenuActiveClassName;


        this.nav = document.createElement("nav");
        this.nav.setAttribute("id",contextMenuId);
        this.nav.setAttribute("class",contextMenuClassName);
        document.getElementsByTagName("body")[0].appendChild(this.nav);
        this.ul = document.createElement("ul");
        this.ul.setAttribute("class",contextMenuUlClassName);
        this.nav.appendChild(this.ul);
        var index;
        for (index = 0; index < item_list.length; index++) {
            var item = item_list[index];
            var li = document.createElement("li");
            li.setAttribute("class",contextMenuItemClassName);
            this.ul.appendChild(li);
            var a = document.createElement("a");
            a.setAttribute("class",contextMenuLinkClassName);
            a.setAttribute("data-id-contextmenu",index);
            a.setAttribute("href","#");
            li.appendChild(a);
            var i = document.createElement("i");
            if (item.class && item.class.strip() != ""){
                i.setAttribute("class",item.class);
            }
            a.appendChild(i);
            var text = document.createTextNode(item.name);
            a.appendChild(text);
        }
        this.menu = document.querySelector("#"+contextMenuId);
        this.menuItems = this.menu.querySelectorAll("."+contextMenuItemClassName);
        this.menuState = 0;

        this.init();
    }
    //////////////////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////
    //
    // H E L P E R    F U N C T I O N S
    //
    //////////////////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////

    /**
     * Function to check if we clicked inside an element with a particular class
     * name.
     *
     * @param {Object} e The event
     * @param {String} className The class name to check against
     * @return {Boolean}
     */
    clickInsideElement(e, className) {
        var el = e.srcElement || e.target;

        if (el.classList.contains(className)) {
            return el;
        } else {
            while (el = el.parentNode) {
                if (el.classList && el.classList.contains(className)) {
                    return el;
                }
            }
        }

        return false;
    }

    clickInsideElementFilter(e, f) {
        var el = e.srcElement || e.target;

        if (f(el)) {
            return el;
        } else {
            while (el = el.parentNode) {
                if (f(el)) {
                    return el;
                }
            }
        }

        return false;
    }

    /**
     * Get's exact position of event.
     *
     * @param {Object} e The event passed in
     * @return {Object} Returns the x and y position
     */
    getPosition(e) {
        var posx = 0;
        var posy = 0;

        if (!e) var e = window.event;

        if (e.pageX || e.pageY) {
            posx = e.pageX;
            posy = e.pageY;
        } else if (e.clientX || e.clientY) {
            posx = e.clientX + document.body.scrollLeft + document.documentElement.scrollLeft;
            posy = e.clientY + document.body.scrollTop + document.documentElement.scrollTop;
        }

        return {
            x: posx,
            y: posy
        }
    }

    //////////////////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////
    //
    // C O R E    F U N C T I O N S
    //
    //////////////////////////////////////////////////////////////////////////////
    //////////////////////////////////////////////////////////////////////////////

    /**
     * Initialise our application's code.
     */
    init() {
        this.contextListener();
        this.clickListener();
        this.keyupListener();
        this.resizeListener();
    }

    /**
     * Listens for contextmenu events.
     */
    contextListener() {
        var self = this;
        document.addEventListener("contextmenu", function (e) {
            self.taskItemInContext = self.clickInsideElementFilter(e, self.filterFunction);

            if (self.taskItemInContext) {
                e.preventDefault();
                self.toggleMenuOn(self);
                self.positionMenu(self,e);
            } else {
                self.taskItemInContext = null;
                self.toggleMenuOff(self);
            }
        });
    }

    /**
     * Listens for click events.
     */
    clickListener() {
        var self = this;
        document.addEventListener("click", function (e) {
            var clickeElIsLink = self.clickInsideElement(e, self.contextMenuLinkClassName);

            if (self.menuState == 1 && clickeElIsLink) {
                e.preventDefault();
                self.menuItemListener(self,clickeElIsLink);
            } else {
                var button = e.which || e.button;
                if (button === 1) {
                    self.toggleMenuOff(self);
                }
            }
        });
    }

    /**
     * Listens for keyup events.
     */
    keyupListener() {
        var self = this;
        window.onkeyup = function (e) {
            if (e.keyCode === 27) {
                self.toggleMenuOff(self);
            }
        }
    }

    /**
     * Window resize event listener
     */
    resizeListener() {
        var self = this;
        window.onresize = function (e) {
            self.toggleMenuOff(self);
        };
    }

    /**
     * Turns the custom context menu on.
     */
    toggleMenuOn(self) {
        if (self.menuState !== 1) {
            self.menuState = 1;
            self.menu.classList.add(self.contextMenuActiveClassName);
        }
    }

    /**
     * Turns the custom context menu off.
     */
    toggleMenuOff(self) {
        if (self.menuState !== 0) {
            self.menuState = 0;
            self.menu.classList.remove(self.contextMenuActiveClassName);
        }
    }

    /**
     * Positions the menu properly.
     *
     * @param {Object} e The event
     */
    positionMenu(self,e) {
        var clickCoords = self.getPosition(e);
        var clickCoordsX = clickCoords.x;
        var clickCoordsY = clickCoords.y;

        var menuWidth = self.menu.offsetWidth + 4;
        var menuHeight = self.menu.offsetHeight + 4;

        var windowWidth = window.innerWidth;
        var windowHeight = window.innerHeight;

        if ((windowWidth - clickCoordsX) < menuWidth) {
            self.menu.style.left = windowWidth - menuWidth + "px";
        } else {
            self.menu.style.left = clickCoordsX + "px";
        }

        if ((windowHeight - clickCoordsY) < menuHeight) {
            self.menu.style.top = windowHeight - menuHeight + "px";
        } else {
            self.menu.style.top = clickCoordsY + "px";
        }
    }

    /**
     * Dummy action function that logs an action when a menu item link is clicked
     *
     * @param {HTMLElement} link The link that was clicked
     */
    menuItemListener(self,link) {
        var clicked_index = parseInt(link.getAttribute("data-id-contextmenu"));
        self.item_list[clicked_index].action(self.taskItemInContext);
        self.toggleMenuOff(self);
    }
}

