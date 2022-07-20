function Random(){
    var num_list = [];
    while(num_list.length < 9){
        var num = Math.ceil(Math.random() * 520);
        if (num_list.includes(num)){
            continue;
        }
        else{
            num_list.push(num);
        }
    } 
    return num_list
}
var num = 0;
function Random2(){
    num = Math.ceil(Math.random() * 520);
    return num;
}