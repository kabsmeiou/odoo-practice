import { mount } from "@odoo/owl";
import { Counter } from "./components/counter";

const placeholder = document.createElement("div");
document.body.appendChild(placeholder);

mount(Counter, { target: placeholder });