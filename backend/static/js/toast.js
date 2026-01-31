/** @format */

// 通用消息提示工具

/**
 * 确保 toast 元素存在于页面中
 */
function ensureToastElementExists() {
	if (!document.getElementById("toastNotification")) {
		// 创建 toast 元素
		const toastHTML = `
            <div id="toastNotification"
                 class="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg p-4 transform translate-y-20 opacity-0 transition-all duration-300 flex items-center z-50">
                <div id="toastIcon"
                     class="w-8 h-8 rounded-full flex items-center justify-center mr-3 bg-primary/10 text-primary">
                    <i class="fa-solid fa-check"></i>
                </div>
                <div>
                    <h4 id="toastTitle" class="font-medium text-neutral-800">操作成功</h4>
                    <p id="toastMessage" class="text-sm text-neutral-600">商品已成功加入购物车</p>
                </div>
                <button id="closeToast" class="ml-4 text-neutral-400 hover:text-neutral-600" onclick="hideToast()">
                    <i class="fa-solid fa-times"></i>
                </button>
            </div>
        `;

		// 将 toast 元素添加到页面中
		document.body.insertAdjacentHTML("beforeend", toastHTML);

		// 添加必要的样式
		const style = document.createElement("style");
		style.textContent = `
            .toast-notification {
                z-index: 9999;
            }
        `;
		document.head.appendChild(style);
	}
}

/**
 * 隐藏通知提示框
 */
function hideToast() {
	const toastNotification = document.getElementById("toastNotification");
	if (toastNotification) {
		toastNotification.classList.add("translate-y-20", "opacity-0");
		toastNotification.classList.remove("translate-y-0", "opacity-100");
	}
}

/**
 * 显示通知提示框
 * @param {string} title - 提示标题
 * @param {string} message - 提示消息
 * @param {boolean} isSuccess - 是否为成功提示，默认为 true
 */
function showToast(title, message, isSuccess = true) {
	// 确保 toast 元素存在
	ensureToastElementExists();

	const toastNotification = document.getElementById("toastNotification");
	const toastTitle = document.getElementById("toastTitle");
	const toastMessage = document.getElementById("toastMessage");
	const toastIcon = document.getElementById("toastIcon");

	if (!toastNotification || !toastTitle || !toastMessage || !toastIcon) {
		console.error("缺少通知提示框的DOM元素");
		return;
	}

	toastTitle.textContent = title;
	toastMessage.textContent = message;

	if (isSuccess) {
		toastIcon.className =
			"w-8 h-8 rounded-full flex items-center justify-center mr-3 bg-green-100 text-green-500";
		toastIcon.innerHTML = '<i class="fa-solid fa-check"></i>';
	} else {
		toastIcon.className =
			"w-8 h-8 rounded-full flex items-center justify-center mr-3 bg-red-100 text-red-500";
		toastIcon.innerHTML = '<i class="fa-solid fa-times"></i>';
	}

	// 显示提示框
	toastNotification.classList.remove("translate-y-20", "opacity-0");
	toastNotification.classList.add("translate-y-0", "opacity-100");

	// 3秒后自动隐藏
	setTimeout(hideToast, 3000);
}

// 页面加载完成后确保 toast 元素存在
document.addEventListener("DOMContentLoaded", ensureToastElementExists);
