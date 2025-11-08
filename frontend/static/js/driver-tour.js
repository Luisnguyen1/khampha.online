// Driver.js Tour Configuration for Main Chat
function initializeDriverTour() {
    const driver = window.driver.js.driver;

    const driverObj = driver({
        showProgress: true,
        showButtons: ['next', 'previous', 'close'],
        nextBtnText: 'Tiếp theo →',
        prevBtnText: '← Quay lại',
        doneBtnText: 'Hoàn thành ✓',
        progressText: '{{current}} / {{total}}',
        popoverClass: 'driverjs-theme',
        steps: [
            {
                element: '#chatSidebar',
                popover: {
                    title: 'Thanh điều hướng',
                    description: 'Đây là thanh điều hướng chính. Bạn có thể truy cập vào các trang: Trang chủ, Chat, Kế hoạch, Discover và Profile.',
                    side: "right",
                    align: 'start'
                }
            },
            {
                element: '#newChatBtn',
                popover: {
                    title: 'Tạo chat mới',
                    description: 'Nhấn vào đây để bắt đầu một cuộc trò chuyện mới. Lịch sử chat cũ của bạn vẫn được lưu bên dưới.',
                    side: "right",
                    align: 'start'
                }
            },
            {
                element: '#chatSessionsList',
                popover: {
                    title: 'Lịch sử Chat',
                    description: 'Tất cả các cuộc trò chuyện trước đây của bạn được lưu ở đây. Nhấn vào bất kỳ cuộc trò chuyện nào để tiếp tục.',
                    side: "right",
                    align: 'start'
                }
            },
            {
                element: '#chatMessages',
                popover: {
                    title: 'Khu vực chat',
                    description: 'Đây là nơi hiển thị cuộc trò chuyện giữa bạn và khampha.online. Tin nhắn của bạn sẽ hiển thị bên phải, còn phản hồi của bot sẽ ở bên trái.',
                    side: "left",
                    align: 'start'
                }
            },
            {
                element: '#messageInput',
                popover: {
                    title: 'Nhập tin nhắn',
                    description: 'Gõ yêu cầu của bạn vào đây. Bạn có thể sử dụng các prefix đặc biệt như @plan (lên kế hoạch), @ask (hỏi đáp), @edit_plan (chỉnh sửa kế hoạch).',
                    side: "top",
                    align: 'start'
                }
            },
            {
                element: '#quickSuggestions',
                popover: {
                    title: 'Gợi ý nhanh',
                    description: 'Nhấn vào các gợi ý này để nhanh chóng bắt đầu trò chuyện mà không cần gõ.',
                    side: "top",
                    align: 'start'
                }
            },
            {
                element: '#sendButton',
                popover: {
                    title: 'Gửi tin nhắn',
                    description: 'Nhấn nút này hoặc Enter để gửi tin nhắn của bạn.',
                    side: "top",
                    align: 'end'
                }
            },
            {
                element: '#planPanel',
                popover: {
                    title: 'Bảng kế hoạch',
                    description: 'Kế hoạch du lịch chi tiết của bạn sẽ được hiển thị ở đây. Bạn có thể lưu, chia sẻ, chỉnh sửa hoặc xem tài liệu tham khảo.',
                    side: "left",
                    align: 'start'
                }
            },
            {
                element: '#savePlanBtn',
                popover: {
                    title: 'Lưu kế hoạch',
                    description: 'Lưu kế hoạch hiện tại vào danh sách kế hoạch của bạn để truy cập sau này. Kế hoạch đã lưu sẽ có sẵn trong trang "Kế hoạch".',
                    side: "bottom",
                    align: 'start'
                }
            },
            {
                element: '#sharePlanBtn',
                popover: {
                    title: 'Chia sẻ kế hoạch',
                    description: 'Chia sẻ kế hoạch du lịch của bạn với bạn bè và gia đình. Bạn có thể sao chép link hoặc chia sẻ trực tiếp qua mạng xã hội.',
                    side: "bottom",
                    align: 'start'
                }
            },
            {
                element: '#editPlanBtn',
                popover: {
                    title: 'Chỉnh sửa kế hoạch',
                    description: 'Chỉnh sửa kế hoạch hiện tại. Bạn có thể thay đổi địa điểm, thời gian, hoạt động hoặc yêu cầu AI điều chỉnh theo ý muốn.',
                    side: "bottom",
                    align: 'start'
                }
            },
            {
                element: '#referencesBtn',
                popover: {
                    title: 'Tài liệu tham khảo',
                    description: 'Xem các nguồn thông tin, bài viết và dữ liệu du lịch được sử dụng để tạo kế hoạch của bạn. Giúp bạn kiểm tra độ tin cậy của thông tin.',
                    side: "bottom",
                    align: 'end'
                }
            },
            {
                element: '#settingsBtn',
                popover: {
                    title: 'Cài đặt',
                    description: 'Tùy chỉnh giao diện, ngôn ngữ, thông báo và các cài đặt khác theo sở thích của bạn.',
                    side: "right",
                    align: 'start'
                }
            },
            {
                popover: {
                    title: 'Hoàn tất! 🎉',
                    description: 'Bạn đã hoàn thành hướng dẫn! Giờ hãy bắt đầu lên kế hoạch du lịch của bạn nhé. Nhấn vào nút Help bất cứ lúc nào để xem lại hướng dẫn này.'
                }
            }
        ],
        onDestroyStarted: () => {
            driverObj.destroy();
        },
    });

    return driverObj;
}

// Function to start the tour
function startDriverTour() {
    const driverObj = initializeDriverTour();
    driverObj.drive();
}

// Export for use in other files
if (typeof window !== 'undefined') {
    window.startDriverTour = startDriverTour;
}
