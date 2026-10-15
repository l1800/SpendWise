import { useContext } from "react"
import { Link } from "react-router-dom"
import { UserContext } from "../context/userContext"
const header=()=>{

    const{user}=useContext(UserContext)
    user!=null&&console.log(user?.status)
    return(<>
    {(!user)&&<h3>ברוכים הבאים לספריה הגדולה בעולם</h3>}
    {user&&<h1>שלום  {user?.firstName}</h1>}
    {user?.status==false&&<button><Link to={"Show"}>הצגת רשימת הספרים </Link></button>}
    {user?.status==false&& <button><Link to={"Lends"}>להצגת ההשאלות שלי</Link></button>} 
    {user?.status&&<button><Link to={"Admin"}>מנהל מערכת</Link></button>}
    {(!user)&&<button> <Link to={"Login"}>כניסה</Link></button>}
    {(!user)&&<button><Link to={"SignUp"}>הרשמה</Link></button>}
    

    </>
    )
}


export default header
