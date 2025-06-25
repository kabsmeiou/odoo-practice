export function choose(list) {
    return list[Math.floor(Math.random() * list.length)];
}

// function to decide if give a reward or not
export function shouldGiveReward() {
    // 1% chance to give a reward
    console.log("Checking if should give reward...");
    return Math.random() < 0.01; // 1% chance to give a reward
}