import { FormController } from "@web/views/form/form_controller";
import { patch } from "@web/core/utils/patch";
import { useClicker } from "../hooks/useClicker";
import { shouldGiveReward } from "../utils/utils";

const FormControllerPatch = {
    setup() {
        super.setup(...arguments);
        if (shouldGiveReward()) {
            const clickService = useClicker();
            clickService.giveReward();
        }
    }
};

patch(FormController.prototype, FormControllerPatch);