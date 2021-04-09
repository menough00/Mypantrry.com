var product="";
function ajax_search(){
    let new_product=$("#product").val();
    if(product!=new_product){
        product=new_product;
        let results_table=$("#product_form")
        let category=$("#category").val();
        let custom=$("#custom").is(":checked");
        if(custom){
            query={method: "POST", url: "/search",
                data:{product: product, category: category, custom: 1}};

        }
        else{
            query={method: "POST", url: "/search",
                data:{product: product, category: category}};
        }
        console.log("query: "+query)
        $.ajax(query).done(function(results){
            results_table.empty();
            $.each(results,function(index){
                let row=$("<tr></tr>");
                row.append($("<td>"+results[index]["name"]+"</td>"));
                results_table.append(row);
            })
        });
    }
}
setInterval(ajax_search,1000);
