export const rewards = [
    {
        description: "Get 1 ClickBot",
        apply(clickerModel) {
            clickerModel.bots.clickBots.count += 1;
            console.log("Increased count!", clickerModel.bots.clickBots.count);
        },
        minLevel: 0,
        maxLevel: 3,
    },
    {
        description: "Get 10 ClickBots",
        apply(clickerModel) {
            clickerModel.bots.clickBots.count += 10;
            console.log("Increased count!", clickerModel.bots.clickBots.count);
        },
        minLevel: 3,
        maxLevel: 4,
    },
    {
        description: "Increase bot power!",
        apply(clickerModel) {
            clickerModel.power.level += 1;
            console.log("Increased power level!", clickerModel.power.level);
        },
        minLevel: 3,
    }
]