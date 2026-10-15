// import { createContext, useState, type ReactNode } from "react";
// import { type User } from "../models/Users";
// export interface userContextType{
//     user:null|User,
//     setUser:(U:User)=>void
// };
// export const UserContext=createContext<userContextType>({user:null,setUser:(s:User)=>{}})
// const UserProvider=({Children}:{Children:ReactNode})=>{
//         const[user,setUser]=useState<User|null>(null);
//         return <UserContext.Provider value={{user,setUser}}>
//             {Children}
//         </UserContext.Provider>
//     };
// export default UserProvider;
import { createContext, useState, type ReactNode } from "react";
import { type User } from "../models/Users"
//import type { FormValues } from "../components/SignUp"
export interface userContextType{
  user: null | User, setUser: (u: User) => void
};
    export const UserContext=createContext<userContextType>({user:null,setUser:(s:User)=>{}})
    
    const UserProvider=({children}:{children:ReactNode})=>{
        const[user,setUser]=useState<User|null>(null);
        return<UserContext.Provider value={{user,setUser}}>
            {children}</UserContext.Provider>
    };
    export default UserProvider;