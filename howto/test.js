function register_wrapper(fn) {
    function return_function() {
        console.log('Before wrapper')
        return fn(...arguments)
        console.log('After wrapper')
    }
    return return_function
}

var some_calc = (numb) => {
    console.log(`Print number  ${numb}`)
}

some_calc = register_wrapper(some_calc)

some_calc(42)