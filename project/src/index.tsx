import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BotTemplate } from "./screens/BotTemplate/BotTemplate";

createRoot(document.getElementById("app") as HTMLElement).render(
  <StrictMode>
    <BotTemplate />
  </StrictMode>,
);
