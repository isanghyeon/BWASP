// true (vector) / false (packet)
let currentState = false;
let implementationSample_attackVector = [
    {
        url: "http://bobmart.com/main.php",
        payloads: ["/class.php", "/korea.php", "/bwasp.php", "/abc.bobmart.com", "/admin.bobmart.com"],
        vulnerability: {
            type: "Cross Site Script(XSS)",
            CVE: [
                {
                    numbering: "2021-0000-111"
                }
            ]
        },
        method: "None",
        date: "2021-09-28 11:00",
        impactRate: 0
    }
];
let implementationSample_packets = [
    {
        url: "http://bobmart.com/main.php",
        payloads: ["/class.php", "/korea.php", "/bwasp.php", "/abc.bobmart.com", "/admin.bobmart.com"],
        packet: "?num= parameter check",
        vulnerability: {
            type: "Cross Site Script(XSS)",
            CVE: [
                {
                    numbering: "2021-0000-111",
                    description: "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
                }
            ]
        },
        method: "None",
        relatedData: ["http://xsstest123456.com/xssprob1.md"],
        date: "2021-09-28 11:00",
        impactRate: 0
    }
];
let idKeyList = [], key = "";

let createKey = () => {
    let gen = () => {
        let key = Math.random().toString(36).substring(2);
        if(!idKeyList.includes(key)) return key;
        else gen()
    }
    return `anonID-${gen()}-${gen()}`;
}

document.getElementById("switchToPacket").addEventListener("click", function(){
    let table = {
        table: document.createElement("table"),
        thead: document.createElement("thead"),
        tbody: document.createElement("tbody")
    };
    currentState = !currentState;
    let status = (currentState) ? "Attack Vector" : "Packets";
    key = Math.random().toString(36).substring(2);
    document.getElementById("titleOfPage").innerHTML = status;
    document.title = `${status} - BWASP`;

    let newThead = document.createElement("tr"),
        element = [
            ["URL", "Vulnerability Doubt", "Method", "Date", "Impact"],
            ["URL", "Packet", "Vulnerability Doubt", "Method", "Related Data", "Date", "Impact"]
        ];

    // Build thead
    element[Number(!currentState)].forEach((columnName)=>{
        let tempThElement = document.createElement("th");
        tempThElement.innerHTML = columnName;
        newThead.appendChild(tempThElement);
    });
    // render thead
    table.thead.appendChild(newThead);

    // Build tbody
    let buildData = (currentState) ? implementationSample_attackVector : implementationSample_packets;
    for (let count = 0; count < buildData.length; count++) {
        let frame = document.createElement("tr");
        let localData = buildData[count], element = Object();
        // URL
        let idKey = createKey();
        element["url"] = {
            parent: document.createElement("td"),
            child: {
                url: document.createElement("a"),
                dropdown: {
                    parent: document.createElement("div"),
                    child: {
                        title: document.createElement("p"),
                        contents: document.createElement("ul")
                    }
                }
            }
        };
        let linebreak = document.createElement("br");

        element.url.parent.classList.add("align-middle");

        element.url.child.url.href = `#${idKey}`;
        element.url.child.url.innerHTML = localData.url;
        element.url.child.url.classList.add("d-block", "py-3", "m-0", "font-weight-bold", "text-primary");
        element.url.child.url.setAttribute("data-toggle", "collapse");
        element.url.child.url.setAttribute("role", "button");
        element.url.child.url.setAttribute("aria-expanded", "false")
        element.url.child.url.setAttribute("aria-controls", idKey);

        element.url.child.dropdown.parent.classList.add("collapse");
        element.url.child.dropdown.parent.id = idKey;

        element.url.child.dropdown.child.title.classList.add("font-weight-bold", "mb-1");
        element.url.child.dropdown.child.title.innerText = "Payloads";

        localData.payloads.forEach((payload) => {
            let liElement = document.createElement("li");
            liElement.innerText = payload;
            element.url.child.dropdown.child.contents.appendChild(liElement);
        })
        element.url.child.dropdown.parent.append(
            element.url.child.dropdown.child.title,
            element.url.child.dropdown.child.contents
        );
        element.url.parent.append(
            element.url.child.url,
            element.url.child.dropdown.parent
        );
        frame.appendChild(element.url.parent);

        // Packets
        if(!currentState){
            let packetDOM = document.createElement("td");
            packetDOM.innerText = localData.packet;
            packetDOM.classList.add("align-middle");
            frame.appendChild(packetDOM);
        }

        // Vulnerability doubt
        element["vuln"] = {
            parent: document.createElement("td"),
            child: {
                vulnType: document.createElement("span")
            }
        }
        element.vuln.parent.classList.add("align-middle");
        frame.appendChild(element.vuln.parent);

        // Method
        element["method"] = document.createElement("td");
        element.method.innerText = localData.method;
        element.method.classList.add("align-middle");
        frame.appendChild(element.method);

        // Related
        if(!currentState){
            let relatedData = {
                parent: document.createElement("td"),
                child: document.createElement("div")
            };
            relatedData.parent.classList.add("align-middle");
            localData.relatedData.forEach((data)=>{
                let relatedDOM = document.createElement("a")
                relatedDOM.href = data;
                relatedDOM.innerHTML = data;
                relatedData.child.appendChild(relatedDOM);
            })
            relatedData.parent.appendChild(relatedData.child);
            frame.appendChild(relatedData.parent);
        }

        let date = new Date(localData.date);
        date = date.toISOString().substring(0, 19).split("T")
        date.push("UTC");
        element["date"] = {
            parent: document.createElement("td"),
            child: {
                date: document.createElement("span"),
                time: document.createElement("span")
            }
        }
        element.date.parent.classList.add("align-middle");
        element.date.child.date.classList.add("font-weight-bold");
        element.date.child.date.innerText = date[0];
        element.date.child.time.innerText = `${date[1]} ${date[2]}`;
        element.date.parent.append(
            element.date.child.date,
            linebreak,
            element.date.child.time
        );
        frame.appendChild(element.date.parent);

        // Impact
        element["impact"] = {
            parent: document.createElement("td"),
            child: document.createElement("p")
        };
        let impactData = [];
        switch(localData.impactRate){
            case 0:
                impactData = ["success", "Low"]
                break
            case 1:
                impactData = ["warning", "Normal"]
                break
            case 2:
                impactData = ["danger", "High"]
                break
        }

        element.impact.parent.classList.add("align-middle");
        element.impact.child.classList.add("btn", "btn-icon-split", "p-1", "mb-0", "pl-3", "pr-3", "rounded-pill", `btn-${impactData[0]}`);
        element.impact.child.innerText = impactData[1];

        element.impact.parent.appendChild(element.impact.child);
        frame.appendChild(element.impact.parent);

        table.tbody.appendChild(frame);
    }

    let tableID = createKey(),
        tablePlace = document.getElementById("tablePlace");
    table.table.classList.add("table", "table-bordered");
    table.table.id = tableID;
    table.table.append(
        table.thead,
        table.tbody
    );
    tablePlace.innerHTML = "";
    tablePlace.appendChild(table.table);
    $(`#${tableID}`).DataTable();
})

window.onload = () => document.getElementById("switchToPacket").click();