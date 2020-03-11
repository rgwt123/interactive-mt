/* This calls query.php to translate the input text. */
var lang_pairs = {'pe':['zh']}
var src_langs = ['pe']
var lang_names = {'en':'英语','zh':'中文','pe':'波斯语'}

function split_sentence() {
    var origText = $('#src').val();
    if (!origText || 0 === origText.length)
        return;
    var srcLang = $('#src_select').val();
    var destLang = $('#dest_select').val();
    if (srcLang === destLang) {
        return;
    }
    var query = {
            "text": origText,
            "sourceLang":srcLang,
            "targetLang":destLang};
    var query_json = JSON.stringify(query);
    $.post("api/split",
           query_json,
           function(data) { show_split_sentence(data); },
           "json");
}

function show_split_sentence(data) {
    try {
        if (data['errorCode'] != 0){
            alert('Error' + data['errorCode'] + data['error']);
        }
        else {
            var srcLang = $("#src_select").val();
            var sentences = data['sentences'];
            // Total translation
            var displayarea = document.getElementById("DisplayArea");
            displayarea.innerHTML = "";
            var displaytable = document.createElement("table");
            displaytable.setAttribute("style", "width: 100%; overflow: auto;");
            displayarea.appendChild(displaytable)
            for (var i=0; i<sentences.length; i++)
            {
                var label_tr = document.createElement("tr");
                var label_td = document.createElement("td");
                var label_div = document.createElement("div");
                label_div.textContent = "Sentence #"+(i+1);
                label_td.appendChild(label_div);
                label_tr.appendChild(label_td);
                displaytable.append(label_tr);
                
                var context_tr = document.createElement("tr");
                var left_td = document.createElement("td");
                var right_td = document.createElement("td");
                var left_textarea = document.createElement("textarea");
                left_textarea.setAttribute("class", "itextarea editarea");
                left_textarea.setAttribute("id", "isrc"+i);
                left_textarea.textContent = sentences[i];
                if (srcLang === "pe"){
                    left_textarea.style.direction = 'rtl';
                }
                else{
                    left_textarea.style.direction = 'ltr';
                }
                var right_textarea = document.createElement("textarea");
                right_textarea.setAttribute("class", "itextarea editarea");
                right_textarea.setAttribute("id", "itrg"+i);
                right_textarea.setAttribute("uniqueid", i);
                right_textarea.setAttribute("onkeydown", "ikeytranslate(event, this)");
                left_td.appendChild(left_textarea);
                right_td.appendChild(right_textarea);
                context_tr.appendChild(left_td);
                context_tr.appendChild(right_td);
                displaytable.append(context_tr);
                
                var button_tr = document.createElement("tr");
                var itrans_td = document.createElement("td");
                var store_td = document.createElement("td");
                var itrans_button = document.createElement("input");
                var store_button = document.createElement("input");
                itrans_button.setAttribute("class", "ibutton");
                itrans_button.setAttribute("type", "button");
                itrans_button.setAttribute("id", "itrans_button"+i);
                itrans_button.setAttribute("value", "翻 译");
                itrans_button.setAttribute("uniqueid", i);
                itrans_button.setAttribute("onClick", "itranslate(this);");
                store_button.setAttribute("class", "ibutton");
                store_button.setAttribute("type", "button");
                store_button.setAttribute("id", "store_button"+i);
                store_button.setAttribute("value", "保 存");
                store_button.setAttribute("uniqueid", i);
                store_button.setAttribute("onClick", "store_onesentence(this);");
                itrans_td.appendChild(itrans_button);
                store_td.appendChild(store_button);
                button_tr.appendChild(itrans_td);
                button_tr.appendChild(store_td);
                displaytable.appendChild(button_tr);
            }

            var buttons = document.createElement("div");
            buttons.setAttribute("id", "bottom_buttons");
            buttons.setAttribute("class", "bottom_block");
            buttons.setAttribute("id", "bottom_buttons");
            var concat_button = document.createElement("input");
            concat_button.setAttribute("type", "button");
            concat_button.setAttribute("class", "blue_button");
            concat_button.setAttribute("id", "concat_button");
            concat_button.setAttribute("value", "汇 总");
            concat_button.setAttribute("onClick", "concat_all();");
            var storeall_button = document.createElement("input");
            storeall_button.setAttribute("type", "button");
            storeall_button.setAttribute("class", "blue_button");
            storeall_button.setAttribute("id", "storeall_button");
            storeall_button.setAttribute("value", "全部保存");
            storeall_button.setAttribute("onClick", "store_allsentences();");
            buttons.appendChild(concat_button);
            buttons.appendChild(storeall_button);
            displayarea.appendChild(document.createElement("br"))
            displayarea.appendChild(buttons);

            var bottom_areas = document.createElement("div");
            bottom_areas.setAttribute("id", "bottom_areas");
            bottom_areas.setAttribute("class", "bottom_block");
            displayarea.appendChild(bottom_areas);
        }
    }
    catch(exc){
        alert(exc);
        for(key in data){alert(key);}
    }
}

function concat_all(){
    console.log('concat all to be done');
    var bottom_areas = document.getElementById('bottom_areas');
    bottom_areas.innerHTML = '';
    var left_area = document.createElement("textarea");
    left_area.setAttribute("class", "editarea bottom_areas");
    left_area.setAttribute("id", "left_area");
    var right_area = document.createElement("textarea");
    right_area.setAttribute("class", "editarea bottom_areas");
    right_area.setAttribute("id", "right_area");
    left_area.setAttribute("stype", "margin-right:10%;");
    right_area.setAttribute("style", "margin-left:10%;");
    var srcLang = $("#src_select").val();
    if (srcLang === "pe"){
        left_area.style.direction = 'rtl';
    }
    else{
        left_area.style.direction = 'ltr';
    }

    bottom_areas.appendChild(left_area);
    bottom_areas.appendChild(right_area);

    var i = 0;
    var srctext = '';
    var trgtext = '';
    while (true){
        var isrc = $('#isrc'+i)[0];
        var itrg = $('#itrg'+i)[0];
        if (isrc === undefined){
            break
        }
        else{
            srctext += (isrc.value + '\n');
            trgtext += (itrg.value + '\n');
        }
        i += 1;
    }
    left_area.textContent = srctext.trim();
    right_area.textContent = trgtext.trim();

}

function ikeytranslate(e, obj){
    var keycode = e.keyCode || e.which;
    if (keycode === 9){
        itranslate(obj);
        e.preventDefault();
    }
    
}

function itranslate(obj) {
    var id = obj.getAttribute("uniqueid");
    var isrc = $("#isrc"+id).val();
    var itrg = $("#itrg"+id).val();
    var startpositon = $("#itrg"+id)[0].selectionStart;
    var prefix = itrg.substring(0, startpositon);
    var srcLang = $('#src_select').val();
    var destLang = $('#dest_select').val();
    var withtable = 'False';
    if ($('#withtable').is(':checked')) {
        withtable = 'True';
    }
    if (srcLang === destLang) {
        return;
    }
    var query = {
            "text": isrc,
            "prefix": prefix,
            "sourceLang": srcLang,
            "targetLang": destLang,
            "withtable": withtable};
    var query_json = JSON.stringify(query);
    $.post("api/itranslate",
        query_json,
        function(data) { show_itranslate(data, id); },
        "json");
}

/* This processes the request result */
function show_itranslate(data, id) {
    try {
        if (data['errorCode'] != 0){
            $("#itrg"+id).val('Error ' + data['errorCode'] + data['error']);
        }
        else {
            var sentence = data['translation'];
            $("#itrg"+id).val(sentence);
        }
    }
    catch(exc){
        alert(exc);
        for(key in data){alert(key);}
    }
}

function store_onesentence(obj) {
    var id = obj.getAttribute("uniqueid");
    console.log(id);
    var isrc = $("#isrc"+id).val();
    var itrg = $("#itrg"+id).val();
    if (isrc.trim() === '' || itrg.trim() === ''){
        alert('第' + id + '个文本框为空！');
        return
    }
    var srcLang = $('#src_select').val();
    var destLang = $('#dest_select').val();
    if (srcLang === destLang) {
        return;
    }
    var query = {
        "sourceText": isrc,
        "targetText": itrg,
        "sourceLang":srcLang,
        "targetLang":destLang,};
    var query_json = JSON.stringify(query);
    $.post("api/store_onesentence",
    query_json,
    function(data) { show_storeresult(data, id); },
    "json");
}

function store_allsentences() {
    var i = 0;
    while (true){
        console.log(i);
        var store_button = $('#store_button'+i)[0];
        if (store_button === undefined){
            break
        }
        else if (store_button.disabled === true){
            i += 1;
            continue
        }
        else{
            store_onesentence(store_button);
            i += 1;
        }
    }
}

function show_storeresult(data, id){
    if (data['errorCode'] != 0){
        alert('Error:' + data['errorCode'] + '\n第' + id + '个文本框错误：' + data['error']);
    }
    else {
        $("#store_button"+id).val("已保存");
        $("#store_button"+id).attr("disabled",true);
    }
}

function fn_clear(){
    document.getElementById('src').value = "";  //设置textarea的值
    document.getElementById("DisplayArea").innerHTML = "";
}

function upload_table(){
    console.log('upload table');
    $('#load_file').click();
}

function fileImport(){
    var selectedFile = document.getElementById('load_file').files[0];
    var name = selectedFile.name;//读取选中文件的文件名
    var size = selectedFile.size;//读取选中文件的大小
    console.log(name, size);
    var reader = new FileReader();//这是核心,读取操作就是由它完成.
    reader.readAsText(selectedFile, "UTF-8");//读取文件的内容,也可以读取文件的URL
    reader.onload = function (e) {
        //当读取完成后回调这个函数,然后此时文件的内容存储到了result中,直接操作即可
        var filetext = e.target.result;
        var lines = filetext.split('\n');
        var table = {};
        for (var i=0; i<lines.length; i++){
            line = lines[i].trim();
            if (line.length === 0){
                continue
            }
            else{
                line = line.split('\t');
                var src_word = line[0];
                var trg_word = line[1];
                if ((src_word === undefined) || (trg_word === undefined)){
                    alert('文件格式不规范！请检查修改后重新上传。');
                    $('#load_file').val('');
                    return
                }
                table[src_word] = trg_word;
            }  
        }
        if (Object.keys(table).length > 0){
            update_table(table);
        }
        else{
            alert('空文件！请检查。');
        }
    }
    $('#load_file').val('');
}

function update_table(table=undefined){
    var srcLang = $('#src_select').val();
    var destLang = $('#dest_select').val();
    if (srcLang === destLang) {
        return;
    }
    var query = {
        "sourceLang":srcLang,
        "targetLang":destLang};
    if (table !== undefined){
        query["table"] = table;
    }
    var query_json = JSON.stringify(query);
    $.post("api/update_table",
           query_json,
           function(data) { 
               if (data['errorCode'] === 0){
                   console.log(data['info'])
                   alert(data['info']);
               }
               else{
                   console.log(data['error']);
                   alert(data['error']);
               }
            },
           "json");
}

function setupsrclang(){
    var src_select = document.getElementById("src_select");
    for (var i=0; i<src_langs.length; i++){
        var op = document.createElement("option");
        op.setAttribute("value", src_langs[i]);
        op.textContent = lang_names[src_langs[i]];
        src_select.appendChild(op)
    }    
    set_destlang();
}

function set_destlang(){
    var srcLang = $("#src_select").val();
    if (srcLang === "pe"){
        $('#src').css("direction", "rtl");
    }
    else{
        $('#src').css("direction", "ltr");
    }
    var dest_select = document.getElementById("dest_select");
    dest_select.innerHTML = "";
    dest_langs = lang_pairs[srcLang]
    for (var i=0; i<dest_langs.length; i++){
        var op = document.createElement("option");
        op.setAttribute("value", dest_langs[i]);
        op.textContent = lang_names[dest_langs[i]];
        dest_select.appendChild(op)
    } 
}

/* This is run after the page is built */
$(document).ready(function() {
    setupsrclang();
    $('#src').val("");
});
