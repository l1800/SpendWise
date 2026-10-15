import { Link,Outlet } from "react-router-dom";
const admin=()=>{
    return<>
    <hr/>
    <button>
    <Link to={"addBook"}>להוספת ספר</Link>
    </button>
    <Outlet/>
    </>
}
export default admin