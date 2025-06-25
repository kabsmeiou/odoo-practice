import { registry } from "@web/core/registry";

registry.category("command_provider").add("clicker.commands", {
    provide: (env, options) => {
        const results = [];
        const actionService = env.services.action
        const clickerService = env.services['awesome_clicker.clicker_service'];
        results.push({
            id: "awesome_clicker.open_client_action",
            name: "Open Clicker",
            action: () => {
                actionService.doAction({
                    type: "ir.actions.client",
                    tag: "awesome_clicker.client_action_template",
                    target: "new",
                    name: "Clicker"
                });
            },
        });
        results.push({
            id: "awesome_clicker.buy_click_bot",
            name: "Buy 1 ClickBot",
            action: () => {
                clickerService.buyClickBot();
            },
        });
        return results;
    }
});