import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useClicker } from "../hooks/useClicker";
import { ClickValue } from "../click_value/click_value";
import { Notebook } from "@web/core/notebook/notebook";
export class ClientAction extends Component {
    static template = "awesome_clicker.client_action_template";
    static components = { ClickValue, Notebook };
    static props = {};

    setup() {
        this.clickService = useClicker();
    }
}

registry.category("actions").add("awesome_clicker.client_action_template", ClientAction);