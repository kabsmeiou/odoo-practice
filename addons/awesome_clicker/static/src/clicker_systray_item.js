import { Component, useExternalListener } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { ClientAction } from "./client_action/client_action";
import { useClicker } from "./hooks/useClicker";
import { ClickValue } from "./click_value/click_value";
import { Dropdown } from "@web/core/dropdown/dropdown";

export class ClickerSystrayItem extends Component {
    static template = "awesome_clicker.clicker_systray_items_template";
    static components = { ClientAction, ClickValue, Dropdown };
    static props = {};

    setup() {
        this.clickService = useClicker();
        this.actionService = useService("action");
        // listen to the click event on the document.body
        useExternalListener(document.body, "click", this.onClick.bind(this));
    }

    onClick(event) {
        // if triggered by the button add 10
        if (event.target.classList.contains("clicker-button")) {
            this.clickService.incrementClickCount(1000);
            return;
        }
        this.clickService.incrementClickCount();
    }

    openClientAction() {
        this.actionService.doAction({
            type: "ir.actions.client",
            tag: "awesome_clicker.client_action_template",
            target: "new",
            name: "Clickerrr"
        });
    }
}

export const systrayItem = {
    Component: ClickerSystrayItem,
    sequence: 100, 
};

registry.category("systray").add("awesome_clicker.ClickerSystrayItem", systrayItem);
