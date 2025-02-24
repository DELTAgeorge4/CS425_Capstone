document.addEventListener("DOMContentLoaded", async function () {
    await loadAccountInfo();
});

async function loadAccountInfo() {
    try {
        const changePasswordModal = document.getElementById("change-password-modal");
        const resetPasswordModal = document.getElementById("reset-password-modal");

        // const resetPasswordForm = document.getElementById("reset-password-form");


        const closeModalBtn = document.querySelectorAll(".close-btn");

        const usernameIndicator = document.getElementById("username-indicator");
        const roleIndicator = document.getElementById("role-indicator");
        const userTable = document.getElementById("user-table");
        const changePasswordButton = document.getElementById("change-password-button");




        changePasswordButton.addEventListener("click", () => {
            changePasswordModal.style.display = "block";
        });





        window.addEventListener("click", (event) => {
            if (event.target === changePasswordModal) {
                changePasswordModal.style.display = "none";
            }

            if (event.target === resetPasswordModal) {
                resetPasswordModal.style.display = "none";
            }
        });

        // load logged in user's account info
        const roleDataResponse = await fetch("/role", { method: "GET" });

        if (!roleDataResponse.ok) {
            throw new Error("Failed to fetch role data");
        }

        const roleData = await roleDataResponse.json();

        usernameIndicator.textContent = "Username: " + roleData.Username;
        roleIndicator.textContent = "Role: " + roleData.Role;

        // load other user data if admin
        if (roleData.Role === "admin") {
            const userDataResponse = await fetch("/users", { method: "GET" });

            if (!userDataResponse.ok) {
                throw new Error("Failed to fetch user data");
                // console.log("Failed to fetch user data");
            }
            document.querySelector(".hidden").style.display = "block";



            console.log(userDataResponse);
            const usersData = await userDataResponse.json();
            console.log(usersData);

            const resetPasswordForm = document.getElementById("reset-password-form");

            // loads user table
            usersData.users.forEach((user) => {
                console.log(user);

                //create table row with user name, role, and action buttons
                const row = document.createElement("tr");
                const username = document.createElement("td");
                username.textContent = user[0];
                row.appendChild(username);

                const role = document.createElement("td");
                role.textContent = user[1];
                row.appendChild(role);

                const actions = document.createElement("td");
                const deleteButton = document.createElement("button");
                deleteButton.textContent = "Delete";
                const resetPasswordButton = document.createElement("button");
                resetPasswordButton.textContent = "Reset Password";
                actions.appendChild(deleteButton);
                actions.appendChild(resetPasswordButton);
                row.appendChild(actions);

                userTable.appendChild(row);

                //calls the delete user function still needs to be implemented
                deleteButton.addEventListener("click", async () => {
                    console.log("Delete button clicked", user[0]);

                });

                //calls the reset password function
                resetPasswordButton.addEventListener("click", async () => {
                    console.log("Reset Password button clicked", user[0]);
                
                    resetPasswordModal.style.display = "block";
                
                    document.getElementById("reset-password-username").textContent = user[0];
                
                    // Remove existing event listeners to prevent duplicates
                    const newResetPasswordForm = document.getElementById("reset-password-form");
                    newResetPasswordForm.replaceWith(newResetPasswordForm.cloneNode(true));
                    
                    const resetPasswordForm = document.getElementById("reset-password-form");


                    // send form data to the backend
                    resetPasswordForm.addEventListener("submit", async (event) => {
                        event.preventDefault();
                        console.log("Form submitted for user:", user[0]);
                
                        const newPassword = document.getElementById("resetNewPassword").value;
                        const confirmPassword = document.getElementById("resetConfirmPassword").value;
                        const message = document.getElementById("reset-message");


                        // checks if the new password and confirm password match
                        if (newPassword !== confirmPassword) {
                            message.textContent = "New passwords do not match!";
                            message.style.color = "red";
                            return;
                        }
                        
                        // checks if the new password is at least 8 characters long
                        if (newPassword.length < 8) {
                            message.textContent = "New password must be at least 8 characters long!";
                            message.style.color = "red";
                            return;
                        }
                
                        // sends the new password to the backend
                        const resetPasswordResponse = await fetch("/reset-user-password", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify({
                                username: user[0], 
                                newPassword: newPassword
                            }),
                        });
                
                        if (!resetPasswordResponse.ok) {
                            const errorMessage = await resetPasswordResponse.text();
                            message.textContent = errorMessage;
                            message.style.color = "red";
                            return;
                        }
                
                        message.textContent = "Password reset successfully!";
                        message.style.color = "green";
                
                        console.log("Password reset for:", user[0]);
                

                        setTimeout(() => {
                            resetPasswordModal.style.display = "none";
                        }, 1500);
                    });
                });
                

                // closeModalBtn.addEventListener("click", () => {
                // });

                resetPasswordForm.addEventListener("submit", async (event) => {

                    event.preventDefault();
                    console.log("Form submitted", user[0]);

                    const newPassword = document.getElementById("resetNewPassword").value;
                    const confirmPassword = document.getElementById("resetConfirmPassword").value;
                    const message = document.getElementById("reset-message");


                    if (newPassword !== confirmPassword) {
                        message.textContent = "New passwords do not match!";
                        message.style.color = "red";
                        return;
                    }

                    if (newPassword.length < 8) {
                        message.textContent = "New password must be at least 8 characters long!";
                        message.style.color = "red";
                        return;
                    }

                    const resetPasswordResponse = await fetch("/reset-user-password", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({
                            username: user[0],
                            newPassword: newPassword,
                        }),
                    });

                    if (!resetPasswordResponse.ok) {
                        const errorMessage = await resetPasswordResponse.json();
                        message.textContent = errorMessage.detail;
                        message.style.color = "red";
                        return;
                    }

                    message.textContent = "Password reset successfully!";

                    console.log("Form submitted");

                    
                });

        
            });
        }

        closeModalBtn.forEach((btn) => {
            btn.addEventListener("click", () => {
                changePasswordModal.style.display = "none";
                resetPasswordModal.style.display = "none";
            });
        });
        //get form data from modal
        const changePasswordForm = document.getElementById("change-password-form");
        changePasswordForm.addEventListener("submit", async (event) => {
            //simple debug to check if the form is being submitted

            event.preventDefault();


            const oldPassword = document.getElementById("changeOldPassword").value;
            const newPassword = document.getElementById("changeNewPassword").value;
            const confirmPassword = document.getElementById("changeConfirmPassword").value;
            const message = document.getElementById("message");
        
            if (newPassword !== confirmPassword) {
                message.textContent = "New passwords do not match!";
                message.style.color = "red";
                return;
            }
        
            if (newPassword.length < 8) {
                message.textContent = "New password must be at least 8 characters long!";
                message.style.color = "red";
                return;
            }

            const changePasswordResponse = await fetch("/change-password", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    oldPassword,
                    newPassword,
                }),
            });

            if (!changePasswordResponse.ok) {
                const errorMessage = await changePasswordResponse.json();
                // errorMessage = await JSON.parse(errorMessage);

                // const eMessage = await changePasswordResponse.json();
                message.textContent = errorMessage.detail;

                console.log(errorMessage);
                message.style.color = "red";
                return;
            }

            message.textContent = "Password changed successfully!";


            console.log("Form submitted");
        });

        


    } catch (error) {
        console.error("Error loading account info:", error);
        document.getElementById("page-content").innerHTML = "<p>Failed to load account information.</p>";
    }
}
