// Sample TypeScript file with linting issues for testing

interface User {
    name:string;
    age:number;
}

function badFunction(x:number,y:number):number {
    return x+y;
}

// Unused variable
const unused = "this is unused";

// Missing spaces
const value=1+2;

// Semicolons missing (if configured)
const text = "hello"

// Any type usage
const data: any = { foo: "bar" };

// Unused function parameters
function process(user:User, id:string) {
    console.log(user.name);
}
