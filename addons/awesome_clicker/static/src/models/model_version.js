export const MODEL_VERSION = 2.0;
export const migrations = [
    {
        previousVersion: 1.0,
        latestVersion: MODEL_VERSION,
        apply(model) {
            model.trees = {
                pearTree: {
                    price: model.trees?.pearTree?.price || 1000,
                    count: model.trees?.pearTree?.count || 0,
                },
                cherryTree: {
                    price: model.trees?.cherryTree?.price || 1000,
                    count: model.trees?.cherryTree?.count || 0,
                },
                appleTree: {
                    price: 1000,
                    count: 0,
                }
            };
            model.fruits = {
                pear: {
                    count: model.fruits?.pear?.count || 0,
                },
                cherry: {
                    count: model.fruits?.cherry?.count || 0,
                },
                apple: {
                    count: 0,
                }
            };
            console.log("Migrated model to version 2.0");
        }
    }
];

export function migrateModelVersion(model) {
    if (model?.version < MODEL_VERSION) {
        for (const migration of migrations) {
            if (model.version === migration.previousVersion) {
                migration.apply(model);
                model.version = migration.latestVersion;
            }
        }
        model.version = MODEL_VERSION;
    }
    return model;
}