interface IElement
{
    div: HTMLDivElement;
    label: HTMLInputElement;
}

export class Line
{
    public readonly element: IElement;
    public baseX = 0;
    public baseY = 0;
    public targetX = 0;
    public targetY = 0;
    public thicknessPX = 1;
    public color = "black";
    public clickEvents = true;
    // public label = "";

    constructor()
    {
        this.element =
        {
            div: document.createElement("div"),
            label: document.createElement("input")
        }
        this.element.div.appendChild(this.element.label);
        this.element.div.classList.add("line");
        this.element.label.type = "text";
    }

    public Dispose(): void
    {
        this.element.div.remove();
    }

    public Draw(): void
    {
        //Update the line's base position.
        this.element.div.style.left = `${this.baseX}px`;
        this.element.div.style.top = `${this.baseY}px`;

        //Set the line's width to meet with tx and ty.
        const distance = Math.sqrt(
            Math.pow(this.targetX - this.element.div.offsetLeft, 2) +
            Math.pow(this.targetY - this.element.div.offsetTop, 2)
        );
        this.element.div.style.width = `${distance}px`;

        //Rotate the line to the angle between the lines origin and the mouse.
        const radAngle = Math.atan2(this.targetY - this.element.div.offsetTop, this.targetX - this.element.div.offsetLeft);
        this.element.div.style.transform = `rotate(${radAngle}rad) translateY(-50%)`;

        //Update the line's style.
        this.element.div.style.backgroundColor = this.color;
        this.element.div.style.height = `${this.thicknessPX}px`;
        this.element.div.style.pointerEvents = this.clickEvents ? "auto" : "none";

        //Update the line's label.
        //The label should always face upright, regardless of the line's rotation.
        this.element.label.style.transform = `rotate(${-radAngle}rad) translate(-50%, -50%)`;
        // this.element.label.value = this.label; //Set via the element instead.
    }
}
