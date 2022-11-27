//Modified from: https://github.com/ReadieFur/BSDP-Overlay/blob/master/src/assets/js/dragElement.ts
export class Draggable
{
    //#region Static
    private static draggables: Draggable[] = [];

    public static Refresh(): void
    {
        for (let draggable of Draggable.draggables)
            draggable.Dispose();

        document.querySelectorAll(".draggable").forEach(element => new Draggable(element as HTMLElement));
    }

    public static Register(element: HTMLElement): Draggable
    {
        return new Draggable(element, element.parentElement);
    }

    public static GetElementTransforms(element: HTMLElement): Map<string, number>
    {
        //https://stackoverflow.com/questions/42267189/how-to-get-value-translatex-by-javascript
        const results: Map<string, number> = new Map<string, number>();
        const matrix = new WebKitCSSMatrix(window.getComputedStyle(element).transform);

        results.set("scale", matrix.a);
        results.set("translateX", matrix.m41);
        results.set("translateY", matrix.m42);

        return results;
    }
    //#endregion

    private container: HTMLElement;
    private containerScale: number;
    private element: HTMLElement;
    private mouseX: number;
    private mouseY: number;
    private xChange: number;
    private yChange: number;
    // private containerCursorStyle: string;
    // private elementCursorStyle: string;

    constructor(element: HTMLElement, container: HTMLElement | null = null)
    {
        if (container !== null) this.container = container;
        else this.container = document.body;
        this.containerScale = 1;
        this.element = element;
        this.mouseX = 0;
        this.mouseY = 0;
        this.xChange = 0;
        this.yChange = 0;
        // this.containerCursorStyle = this.element.style.cursor;
        // this.elementCursorStyle = this.element.style.cursor;

        this.GetScale();
        new MutationObserver(() => this.GetScale()).observe(this.container, { attributes: true });

        //Event listeners were being a problem here so for now I will be setting only one event to the container (this will stop me from being able to use this event on this element elsewhere).
        this.element.onmousedown = (e: MouseEvent) => this.MouseDownEvent(e);

        Draggable.draggables.push(this);
    }

    public Dispose(): void
    {
        this.element.onmousedown = null;
        this.container.onmouseup = null;
        this.container.onmousemove = null;

        Draggable.draggables.splice(Draggable.draggables.indexOf(this), 1);
    }

    private GetScale(): void
    {
        let scale = Draggable.GetElementTransforms(this.container).get("scale")!;

        if (scale !== undefined && !isNaN(scale))
            this.containerScale = scale;
    }

    private MouseDownEvent(e: MouseEvent): void
    {
        if (this.element.classList.contains("d_ignore_children")
            && e.target !== this.element
            && !(<HTMLElement>e.target).classList.contains("d_grabber"))
            return;

        e.preventDefault();

        // this.containerCursorStyle = this.container.style.cursor;
        // this.elementCursorStyle = this.element.style.cursor;
        // this.container.style.cursor = "none";
        // this.element.style.cursor = "none";

        this.element.style.left = `${this.element.offsetLeft}px`;
        this.element.style.top = `${this.element.offsetTop}px`;
        this.container.onmouseup = () => this.MouseUpEvent();

        //Remove the elements right/bottom position and replace it back to left/top.
        //Set mouse position when the mouse is first down.
        this.mouseX = e.clientX;
        this.mouseY = e.clientY;
        //If using element instead of the container, if the mouse moves fast enough to escape the element before its position is updated, it will stop updating the elements position until the mouse goes over the element again.
        this.container.onmousemove = (_e: MouseEvent) => this.MouseMoveEvent(_e);
    }

    private MouseUpEvent(): void
    {
        //Stop moving when the mouse is released.
        this.container.onmouseup = null;
        this.container.onmousemove = null;

        // this.container.style.cursor = this.containerCursorStyle;
        // this.element.style.cursor = this.elementCursorStyle;
    }

    private MouseMoveEvent(e: MouseEvent): void
    {
        e.preventDefault();

        //Calculate the change in mouse position.
        //The scale application isn't perfect but it will do.
        this.xChange = (this.mouseX - e.clientX) / this.containerScale;
        this.yChange = (this.mouseY - e.clientY) / this.containerScale;
        //Set the new position of the mouse.
        this.mouseX = e.clientX;
        this.mouseY = e.clientY;

        const transforms = Draggable.GetElementTransforms(this.element);

        //Move the element to the new position.
        let elementLeft: number;
        if (this.element.offsetLeft + this.element.clientWidth + transforms.get("translateX")! > this.container.clientWidth)
            elementLeft = this.container.clientWidth - this.element.clientWidth - transforms.get("translateX")!;
        else if (this.element.offsetLeft < 0)
            elementLeft = 0;
        else
            elementLeft = this.element.offsetLeft - this.xChange;
        this.element.style.left = `${elementLeft}px`;

        let elementTop: number;
        if (this.element.offsetTop + this.element.clientHeight + transforms.get("translateY")! > this.container.clientHeight)
            elementTop = this.container.clientHeight - this.element.clientHeight - transforms.get("translateY")!;
        else if (this.element.offsetTop < 0)
            elementTop = 0;
        else
            elementTop = this.element.offsetTop - this.yChange;
        this.element.style.top = `${elementTop}px`;

        this.element.dispatchEvent(new CustomEvent("dragging", { bubbles: true }));
    }
}
