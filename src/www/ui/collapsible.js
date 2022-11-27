export class Collapsible {
    static Refresh() {
        for (const collapsible of document.querySelectorAll(".collapsible")) {
            if (collapsible.childElementCount !== 2)
                continue;
            const element = {
                root: collapsible,
                header: collapsible.children[0],
                content: collapsible.children[1]
            };
            if (!collapsible.classList.contains("c_active") && getComputedStyle(element.root)["visibility"] === "visible")
                this.Collapse(element);
            else if (collapsible.classList.contains("c_active") && getComputedStyle(element.root)["visibility"] !== "visible")
                this.Expand(element);
            element.header.onclick = () => {
                if (collapsible.classList.contains("c_active"))
                    this.Collapse(element);
                else
                    this.Expand(element);
            };
        }
    }
    static Expand(element) {
        element.root.classList.add("c_active");
        element.content.style.visibility = "visible";
        element.content.style.height = element.content.scrollHeight + "px";
    }
    static Collapse(element) {
        element.root.classList.remove("c_active");
        element.content.style.visibility = "collapse";
        element.content.style.height = "0px";
    }
}
//# sourceMappingURL=collapsible.js.map