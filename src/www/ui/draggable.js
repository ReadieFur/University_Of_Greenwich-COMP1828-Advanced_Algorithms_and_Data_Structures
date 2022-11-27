export class Draggable {
    static Refresh() {
        for (let draggable of Draggable.draggables)
            draggable.Dispose();
        document.querySelectorAll(".draggable").forEach(element => new Draggable(element));
    }
    static Register(element) {
        return new Draggable(element, element.parentElement);
    }
    static GetElementTransforms(element) {
        const results = new Map();
        const matrix = new WebKitCSSMatrix(window.getComputedStyle(element).transform);
        results.set("scale", matrix.a);
        results.set("translateX", matrix.m41);
        results.set("translateY", matrix.m42);
        return results;
    }
    constructor(element, container = null) {
        if (container !== null)
            this.container = container;
        else
            this.container = document.body;
        this.containerScale = 1;
        this.element = element;
        this.mouseX = 0;
        this.mouseY = 0;
        this.xChange = 0;
        this.yChange = 0;
        this.GetScale();
        new MutationObserver(() => this.GetScale()).observe(this.container, { attributes: true });
        this.element.onmousedown = (e) => this.MouseDownEvent(e);
        Draggable.draggables.push(this);
    }
    Dispose() {
        this.element.onmousedown = null;
        this.container.onmouseup = null;
        this.container.onmousemove = null;
        Draggable.draggables.splice(Draggable.draggables.indexOf(this), 1);
    }
    GetScale() {
        let scale = Draggable.GetElementTransforms(this.container).get("scale");
        if (scale !== undefined && !isNaN(scale))
            this.containerScale = scale;
    }
    MouseDownEvent(e) {
        if (this.element.classList.contains("d_ignore_children")
            && e.target !== this.element
            && !e.target.classList.contains("d_grabber"))
            return;
        e.preventDefault();
        this.element.style.left = `${this.element.offsetLeft}px`;
        this.element.style.top = `${this.element.offsetTop}px`;
        this.container.onmouseup = () => this.MouseUpEvent();
        this.mouseX = e.clientX;
        this.mouseY = e.clientY;
        this.container.onmousemove = (_e) => this.MouseMoveEvent(_e);
    }
    MouseUpEvent() {
        this.container.onmouseup = null;
        this.container.onmousemove = null;
    }
    MouseMoveEvent(e) {
        e.preventDefault();
        this.xChange = (this.mouseX - e.clientX) / this.containerScale;
        this.yChange = (this.mouseY - e.clientY) / this.containerScale;
        this.mouseX = e.clientX;
        this.mouseY = e.clientY;
        const transforms = Draggable.GetElementTransforms(this.element);
        let elementLeft;
        if (this.element.offsetLeft + this.element.clientWidth + transforms.get("translateX") > this.container.clientWidth)
            elementLeft = this.container.clientWidth - this.element.clientWidth - transforms.get("translateX");
        else if (this.element.offsetLeft < 0)
            elementLeft = 0;
        else
            elementLeft = this.element.offsetLeft - this.xChange;
        this.element.style.left = `${elementLeft}px`;
        let elementTop;
        if (this.element.offsetTop + this.element.clientHeight + transforms.get("translateY") > this.container.clientHeight)
            elementTop = this.container.clientHeight - this.element.clientHeight - transforms.get("translateY");
        else if (this.element.offsetTop < 0)
            elementTop = 0;
        else
            elementTop = this.element.offsetTop - this.yChange;
        this.element.style.top = `${elementTop}px`;
        this.element.dispatchEvent(new CustomEvent("dragging", { bubbles: true }));
    }
}
Draggable.draggables = [];
//# sourceMappingURL=draggable.js.map