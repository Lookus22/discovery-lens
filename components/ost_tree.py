import streamlit.components.v1 as components

def render_ost_tree(goal, opportunities):

    opps_html = ""
    for opp in opportunities:
        sols_html = ""
        for sol in opp.get("solutions", []):
            sols_html += f'<div class="sol-node">{sol["label"]}</div>'

        opps_html += f"""
        <div class="opp-col">
            <div class="opp-node">
                {opp["jtbd"]}
                <div class="opp-score">priority {opp.get("priority_score", 0):.2f}</div>
            </div>
            <div class="sols-col">{sols_html}</div>
            <div class="opp-connector-v"></div>
        </div>
        """

    html = f"""
    <style>
        body {{ font-family: sans-serif; margin: 0; padding: 10px; }}
        .goal-node {{
            background: #534AB7;
            color: #EEEDFE;
            border-radius: 10px;
            padding: 14px 20px;
            font-size: 14px;
            font-weight: 500;
            text-align: center;
            max-width: 600px;
            margin: 0 auto;
        }}
        .connector-v {{
            width: 2px;
            height: 24px;
            background: #888;
            margin: 0 auto;
        }}
        .opp-connector-v {{
            width: 2px;
            height: 16px;
            background: #888;
            margin: 0 auto;
        }}
        .opps-row {{
            display: grid;
            grid-template-columns: repeat({len(opportunities) or 4}, 1fr);
            gap: 10px;
        }}
        .opp-col {{
            display: flex;
            flex-direction: column;
            align-items: center;
        }}
        .opp-node {{
            background: #E1F5EE;
            border: 1px solid #5DCAA5;
            border-radius: 8px;
            padding: 10px;
            font-size: 12px;
            font-weight: 500;
            color: #085041;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
        }}
        .opp-score {{
            font-size: 11px;
            color: #0F6E56;
            margin-top: 4px;
        }}
        .sols-col {{
            display: flex;
            flex-direction: column;
            gap: 6px;
            width: 100%;
        }}
        .sol-node {{
            background: #FAECE7;
            border: 1px solid #F0997B;
            border-radius: 8px;
            padding: 8px;
            font-size: 11px;
            color: #4A1B0C;
            text-align: center;
            width: 100%;
            box-sizing: border-box;
        }}
    </style>

    <div class="goal-node">{goal}</div>
    <div class="connector-v"></div>
    <div class="opps-row">{opps_html}</div>
    """

    components.html(html, height=400)