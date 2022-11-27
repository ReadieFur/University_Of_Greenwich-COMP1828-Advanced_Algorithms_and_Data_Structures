export interface ICollapsibleElement
{
    root: HTMLElement;
    header: HTMLElement;
    content: HTMLElement;
}

export class Collapsible
{
    public static Refresh(): void
    {
        for (const collapsible of document.querySelectorAll(".collapsible"))
        {
            if (collapsible.childElementCount !== 2)
                continue;

            const element: ICollapsibleElement =
            {
                root: collapsible as HTMLElement,
                header: collapsible.children[0] as HTMLElement,
                content: collapsible.children[1] as HTMLElement
            };

            if (!collapsible.classList.contains("c_active") && getComputedStyle(element.root)["visibility"] === "visible")
                this.Collapse(element);
            else if (collapsible.classList.contains("c_active") && getComputedStyle(element.root)["visibility"] !== "visible")
                this.Expand(element);

            element.header.onclick = () =>
            {
                if (collapsible.classList.contains("c_active"))
                    this.Collapse(element);
                else
                    this.Expand(element);
            };
        }
    }

    public static Expand(element: ICollapsibleElement)
    {
        element.root.classList.add("c_active");
        element.content.style.visibility = "visible";
        element.content.style.height = element.content.scrollHeight + "px";
    }

    public static Collapse(element: ICollapsibleElement): void
    {
        element.root.classList.remove("c_active");
        element.content.style.visibility = "collapse";
        element.content.style.height = "0px";
    }
}
