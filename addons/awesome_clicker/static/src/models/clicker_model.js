import { Reactive } from "@web/core/utils/reactive";
import { EventBus } from "@odoo/owl";
import { choose } from "../utils/utils";
import { rewards } from "../lib/click_rewards";
import { MODEL_VERSION } from "./model_version";
export class ClickerModel extends Reactive {
    constructor() {
        super();
        this.version = MODEL_VERSION; // Version number for state management
        this.clickCount = 0; // Total clicks
        this.bots = {
            clickBots: {
                price: 1000,
                clicksPerBot: 10,
                count: 0,
            },
            bigClickBots: {
                price: 5000,
                clicksPerBot: 100,
                count: 0,
            },
        };
        this.level = 0;
        this.trees = {
            pearTree: {
                price: 1000,
                count: 0,
            },
            cherryTree: {
                price: 1000,
                count: 0,
            },
            appleTree: {
                price: 1000,
                count: 0,
            }
        },
        this.fruits = {
            pear: {
                count: 0,
            },
            cherry: {
                count: 0,
            },
            apple: {
                count: 0,
            }
        }
        this.power = {
            level: 1,
            price: 100000,
        };
        this.eventBus = new EventBus();
    }

    static loadState(state) {
        const clicker = new ClickerModel();
        const clickerInstance = Object.assign(clicker, state);
        // reinitialize the eventBus
        clickerInstance.eventBus = new EventBus();
        return clickerInstance;
    }

    executeBots() {
        this.clickCount += this.bots.clickBots.count * this.bots.clickBots.clicksPerBot * this.power.level; // 10 clicks per bot
        this.clickCount += this.bots.bigClickBots.count * this.bots.bigClickBots.clicksPerBot * this.power.level; // 100 clicks per big bot
    }

    harvestFruits() {
        this.fruits.pear.count += this.trees.pearTree.count;
        this.fruits.cherry.count += this.trees.cherryTree.count;
        this.fruits.apple.count += this.trees.appleTree.count;
    }

    getTotalTrees() {
        return this.trees.pearTree.count + this.trees.cherryTree.count;
    }

    getTotalFruits() {
        return this.fruits.pear.count + this.fruits.cherry.count;
    }

    incrementClickCount(amount = 1) {
        this.clickCount += amount;
        if (this.level < 1 && this.clickCount >= 1000) {
            this.eventBus.trigger("MILESTONE_1k");
            this.level += 1;
        }
        if (this.level < 2 && this.clickCount >= 5000) {
            this.eventBus.trigger("MILESTONE_5k");
            this.level += 1;
        }
        if (this.level < 2 && this.clickCount >= (100000)) {
            this.eventBus.trigger("MILESTONE_100k");
            this.level += 1;
        }
    }

    buyBot(botType) {
        if (!this.bots[botType]) {
            console.error(`Bot type ${botType} does not exist.`);
            return;
        }
        if (this.clickCount < this.bots[botType].price) {
            console.log(`Not enough clicks to buy a ${botType}. You need at least ${this.bots[botType].price} clicks.`);
            return;
        }
        this.bots[botType].count += 1;
        this.clickCount -= this.bots[botType].price;
        console.log(`Bought a ${botType}. Total count: ${this.bots[botType].count}`);
    }

    buyPowerUpgrade() {
        if (this.clickCount < this.power.price) {
            console.log("Not enough clicks to buy a Power Upgrade. You need at least 100000 clicks.");
            return;
        }
        this.power.level += 1; // Increase power by 1
        this.clickCount -= this.power.price;
    }

    buyTree(treeType) {
        if (!this.trees[treeType]) {
            console.error(`Tree type ${treeType} does not exist.`);
            return;
        }
        if (this.clickCount < this.trees[treeType].price) {
            console.log(`Not enough clicks to buy a ${treeType}. You need at least ${this.trees[treeType].price} clicks.`);
            return;
        }
        this.trees[treeType].count += 1;
        this.clickCount -= this.trees[treeType].price;
    }

    addClickBot(count) {
        if (count <= 0) {
            console.error("Count must be a positive number.");
            return;
        }
        this.bots.clickBots.count += count;
    }

    giveReward() {
        // get eligible rewards based on the current level
        const eligibleRewards = rewards.filter(reward => {
            return this.level >= reward.minLevel && (reward.maxLevel === undefined || this.level <= reward.maxLevel);
        });
        const reward = choose(eligibleRewards)
        this.eventBus.trigger("REWARD", reward);
        return reward;
    }
}