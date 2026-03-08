const TRACE_INTERVAL = 3000;

// Покроково кодує історію документу
//
class Trace {

    constructor() {
        this.diffs = [];
        this.lastText = "";
    }

    // Екземпляр траси з масиву різниць
    //
    static fromDifferences(diffs) {
        const trace = new Trace();
        trace.diffs = diffs;
        const shots = trace.decode();
        trace.lastText = shots[shots.length - 1][0];
        return trace;
    }


    toJson() {
        return JSON.stringify(this.diffs);
    }

    // Додає текст до траси
    //
    addText(text) {
        this.diffs.push(this._difference(text));
        this.lastText = text;
    }

    // Додає коментар до траси
    //
    addComment(comment) {
        this.diffs.push([comment]);
    }
    
    // Різниця двох текстів t2 - t1
    //
    _difference(t2)  {
        let t1 = this.lastText;
        if (t1 === t2)
            return [];
        let l = 0;
        while (t1[l] === t2[l]) 
            l++;
        let r = 0;
        while (t1[t1.length - 1 - r] === t2[t2.length - 1 - r]) 
            r++;
        let mid = r ? t2.slice(l, -r) : t2.slice(l);
        return [l, mid, r];
    }

    // Розгортає трасу у масив пар (text, comment)
    decode() {
        const pairs = [];
        let text = "";
        for (let slide of this.diffs) {
            if (slide.length == 3)  
            {
                const [l, mid, r] = slide;
                const left = text.slice(0, l);
                const right = r ? text.slice(-r) : "";
                text = left + mid + right;
                pairs.push([text, ""]);

            } 
            else if (slide.length == 0) 
            {
                pairs.push([text, ""])
            }
            // add comment to last pair
            else if (slide.length == 1) 
            {
                if (pairs.length > 0) {
                    pairs[pairs.length - 1][1] = slide[0] 
                }
            }
        }
        return pairs;
    }
}
