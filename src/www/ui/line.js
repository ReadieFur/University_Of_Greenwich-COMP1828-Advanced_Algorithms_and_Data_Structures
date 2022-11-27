export class Line {
    constructor() {
        this.baseX = 0;
        this.baseY = 0;
        this.targetX = 0;
        this.targetY = 0;
        this.thicknessPX = 1;
        this.color = "black";
        this.clickEvents = true;
        this.element =
            {
                div: document.createElement("div"),
                label: document.createElement("input")
            };
        this.element.div.appendChild(this.element.label);
        this.element.div.classList.add("line");
        this.element.label.type = "text";
    }
    Dispose() {
        this.element.div.remove();
    }
    Draw() {
        this.element.div.style.left = `${this.baseX}px`;
        this.element.div.style.top = `${this.baseY}px`;
        const distance = Math.sqrt(Math.pow(this.targetX - this.element.div.offsetLeft, 2) +
            Math.pow(this.targetY - this.element.div.offsetTop, 2));
        this.element.div.style.width = `${distance}px`;
        const radAngle = Math.atan2(this.targetY - this.element.div.offsetTop, this.targetX - this.element.div.offsetLeft);
        this.element.div.style.transform = `rotate(${radAngle}rad) translateY(-50%)`;
        this.element.div.style.backgroundColor = this.color;
        this.element.div.style.height = `${this.thicknessPX}px`;
        this.element.div.style.pointerEvents = this.clickEvents ? "auto" : "none";
        this.element.label.style.transform = `rotate(${-radAngle}rad) translate(-50%, -50%)`;
    }
}
//# sourceMappingURL=line.js.map