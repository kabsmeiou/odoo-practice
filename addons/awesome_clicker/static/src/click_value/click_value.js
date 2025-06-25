import { Component } from "@odoo/owl";
import { humanNumber } from "@web/core/utils/numbers";
import { useClicker } from "../hooks/useClicker";
export class ClickValue extends Component {
    static template = "awesome_clicker.click_value_template";

    static props = {};

    setup() {
        this.clickService = useClicker();
    }

    get humanizedClickCount() {
        return humanNumber(this.clickService.clickCount, {
            decimals: 1,
        });
    }
}
