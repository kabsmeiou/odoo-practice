import { registry } from "@web/core/registry";
import { ClickerModel } from "../models/clicker_model";
import { browser } from "@web/core/browser/browser";
import { migrateModelVersion } from "../models/model_version";

const clickerService = {
    dependencies: ["action", "effect", "notification"],
    start (env, services) {
        const localState = browser.localStorage.getItem("clicker_state");
        const parsedState = migrateModelVersion(JSON.parse(localState));
        const clickerModel = parsedState ? ClickerModel.loadState(parsedState) : new ClickerModel();

        setInterval(() => {
            clickerModel.executeBots();
        }, 1000 * 10);

        setInterval(() => {
            browser.localStorage.setItem("clicker_state", JSON.stringify(clickerModel));
        }, 1000 * 8); // Save every 8 seconds

        setInterval(() => {
            clickerModel.harvestFruits();
        }, 1000 * 30); // 30 seconds

        const bus = clickerModel.eventBus;
        bus.addEventListener("MILESTONE_1k", () => {
            services.effect.add({
                message: "You just leveled up!",
                type: "rainbow_man",
            });
        });
        bus.addEventListener("MILESTONE_5k", () => {
            services.effect.add({
                message: "You just leveled up again!",
                type: "rainbow_man",
            });
        });
        bus.addEventListener("MILESTONE_100k", () => {
            services.effect.add({
                message: "You just leveled up again! You are now eligible to buy a Power Upgrade!",
                type: "rainbow_man",
            });
        });
        bus.addEventListener("REWARD", (ev) => {
            const reward = ev.detail;
            const closeNotification = services.notification.add(
                `You received a reward: ${reward.description}`,
                {
                    type: "success",
                    sticky: true,
                    buttons: [{
                        name: "Collect",
                        onClick: () => {
                            reward.apply(clickerModel);
                            closeNotification();
                            services.action.doAction({
                                type: "ir.actions.client",
                                tag: "awesome_clicker.client_action_template",
                                target: "new",
                                name: "Clicker Rewards",
                            });
                        },
                    }],
                }
            );
        });
        return clickerModel;
    },
};

registry.category("services").add("awesome_clicker.clicker_service", clickerService);
